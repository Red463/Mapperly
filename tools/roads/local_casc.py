"""Small independent, read-only reader for this build's local CASC snapshot.

Standard library only. No network, executable dependencies, or game-install writes.
Byte layout references: wowdev.wiki/CASC and CascLib's documented root structs.
Supports modern TSFM version-2 root, EN v1, IDX v7 and N/Z BLTE only.
"""
from pathlib import Path
import array
import bisect
import hashlib
import struct
import zlib


class LocalCasc:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.data_dir = self.root / 'snapshot/Data/data'
        cache = self.root / 'cache/tpr/wow/data'
        self.encoding = (cache / '2a01a11b27b671e7267422343915bc08.decoded').read_bytes()
        r = (cache / 'f62d4bbd5ad37e073fd8b6415d66f11d.decoded').read_bytes()
        if r[:4] != b'TSFM' or struct.unpack_from('<I', r, 8)[0] != 2:
            raise ValueError('Expected this snapshot TSFM root version 2')
        self.root_bytes = r
        self.groups = []
        p = struct.unpack_from('<I', r, 4)[0]
        while p < len(r):
            count, locale, flags1, flags2, flags3 = struct.unpack_from('<IIIIB', r, p)
            p += 17
            ids = array.array('I')
            ids.frombytes(r[p:p + count * 4])
            if __import__('sys').byteorder != 'little':
                ids.byteswap()
            previous = -1
            for i, delta in enumerate(ids):
                previous += delta + 1
                ids[i] = previous
            p += count * 4
            keys_at = p
            p += count * 16
            flags = flags1 | flags2 | (flags3 << 17)
            if not flags & 0x10000000:
                p += count * 8
            if p > len(r):
                raise ValueError('Root group exceeds file')
            if not flags & 0x180 and (locale == 0 or locale & 0x202):
                self.groups.append((ids, keys_at))
        e = self.encoding
        if e[:5] != b'EN\x01\x10\x10':
            raise ValueError('Unsupported encoding header')
        self.page_size = int.from_bytes(e[5:7], 'big') * 1024
        self.page_count = int.from_bytes(e[9:13], 'big')
        self.table_at = 22 + int.from_bytes(e[18:22], 'big')
        self.pages_at = self.table_at + self.page_count * 32
        self.first_keys = [e[self.table_at+i*32:self.table_at+i*32+16] for i in range(self.page_count)]
        self.index = {}
        latest = {}
        for path in self.data_dir.glob('*.idx'):
            bucket = path.stem[:2]
            if bucket not in latest or path.name > latest[bucket].name:
                latest[bucket] = path
        for path in latest.values():
            b = path.read_bytes()
            if b[8:10] != b'\x07\x00' or b[12:16] != b'\x04\x05\x09\x1e':
                raise ValueError('Unsupported local IDX layout')
            length = struct.unpack_from('<I', b, 32)[0]
            if length % 18 or 40 + length > len(b):
                raise ValueError('Invalid IDX entries')
            for p in range(40, 40 + length, 18):
                packed = int.from_bytes(b[p+9:p+14], 'big')
                self.index[b[p:p+9]] = (packed >> 30, packed & ((1 << 30)-1), int.from_bytes(b[p+14:p+18], 'little'))

    def ckey_for_fdid(self, fdid):
        for ids, offset in self.groups:
            i = bisect.bisect_left(ids, fdid)
            if i < len(ids) and ids[i] == fdid:
                return self.root_bytes[offset+i*16:offset+(i+1)*16]
        raise KeyError(f'FileDataID {fdid} absent from selected root locales')

    def ekeys_for_ckey(self, ckey):
        page = bisect.bisect_right(self.first_keys, ckey)-1
        if page < 0:
            raise KeyError(ckey.hex())
        p = self.pages_at + page*self.page_size
        end = p + self.page_size
        e = self.encoding
        while p < end and e[p]:
            count = e[p]
            key = e[p+6:p+22]
            if key == ckey:
                return [e[p+22+i*16:p+38+i*16] for i in range(count)]
            p += 22+16*count
        raise KeyError(f'CKey {ckey.hex()} absent from encoding page')

    @staticmethod
    def decode_blte(b):
        if b[:4] != b'BLTE':
            raise ValueError('Missing BLTE signature')
        header_size = int.from_bytes(b[4:8], 'big')
        def decode(chunk):
            if chunk[:1] == b'N':
                return chunk[1:]
            if chunk[:1] == b'Z':
                return zlib.decompress(chunk[1:])
            raise ValueError(f'Unsupported BLTE mode {chunk[:1]!r}')
        if header_size == 0:
            return decode(b[8:])
        count = int.from_bytes(b[9:12], 'big')
        if header_size != 12+24*count:
            raise ValueError('Invalid BLTE chunk table')
        p = header_size
        output = []
        for i in range(count):
            at = 12+24*i
            compressed, expanded = struct.unpack_from('>II', b, at)
            chunk = b[p:p+compressed]
            if len(chunk) != compressed or hashlib.md5(chunk).digest() != b[at+8:at+24]:
                raise ValueError('BLTE chunk checksum mismatch')
            decoded = decode(chunk)
            if len(decoded) != expanded:
                raise ValueError('BLTE expanded size mismatch')
            output.append(decoded)
            p += compressed
        return b''.join(output)

    def read_fdid(self, fdid):
        ckey = self.ckey_for_fdid(fdid)
        for ekey in self.ekeys_for_ckey(ckey):
            if ekey[:9] not in self.index:
                continue
            archive, offset, size = self.index[ekey[:9]]
            with (self.data_dir / f'data.{archive:03d}').open('rb') as f:
                f.seek(offset)
                envelope = f.read(size)
            result = self.decode_blte(envelope[30:])
            if hashlib.md5(result).digest() != ckey:
                raise ValueError('Decoded content CKey mismatch')
            return result
        raise FileNotFoundError(f'FileDataID {fdid}: encoded data absent from local snapshot')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('fdid', type=int, nargs='+')
    args = parser.parse_args()
    casc = LocalCasc(args.root)
    for fdid in args.fdid:
        content = casc.read_fdid(fdid)
        print(f'{fdid} {len(content)} {content[:4]!r} sha256={hashlib.sha256(content).hexdigest()}')
