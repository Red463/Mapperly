"""Validate verified stock, in-game item art and the reference town against the shipped Lua."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / '.test-deps'))
import build_vendor_goods as goods
from lupa.lua51 import LuaRuntime


class VendorGoodsTests(unittest.TestCase):
    def test_filter_stock_independent_of_sql_order(self):
        def listing(item, kind=1, condition=0):
            return 'npc_vendor', dict(entry=4182, item=item, type=kind, PlayerConditionID=condition)
        condition = ('conditions', dict(SourceTypeOrReferenceId=23, SourceGroup=4182, SourceEntry=111))
        rows = [condition, listing(111), listing(112, condition=13), listing(113, kind=2),
                listing(-114), listing(2515), listing(2515)]
        self.assertEqual(goods.regular_stock(rows, {4182}), {4182: {2515}})
        self.assertEqual(goods.regular_stock(reversed(rows), {4182}), {4182: {2515}})
        self.assertEqual(goods.regular_stock(rows, {999}), {})

    def test_food_drink_and_reagent_types(self):
        self.assertEqual(goods.category(0,5,0,[(59,'')]),'drink')
        self.assertEqual(goods.category(0,5,0,[(0,'Strong Alcohol')]),'drink')
        self.assertEqual(goods.category(0,5,0,[(11,'')]),'food')
        self.assertEqual(goods.category(0,5,4,[]),'food')
        self.assertEqual(goods.category(0,5,0,[]),'consumables')
        self.assertEqual(goods.category(15,1,0,[]),'reagents')
        self.assertEqual(goods.category(5,0,0,[]),'reagents')

    def test_reference_town_and_integrity(self):
        lua = LuaRuntime(unpack_returned_tuples=True)
        lua.execute('A={}')
        for path in ('Data/ServiceDirectory.lua','Data/VendorGoods.lua'):
            lua.execute('assert(loadstring(...))("Mapperly", A)', (ROOT/path).read_text(encoding='utf-8'))
        lua.execute("""
        local items,stock=A.VendorGoods.items,A.VendorGoods.stock
        local function sells(npc,id)
            for _,item in ipairs(stock[npc] or {}) do if item==id then return true end end
            return false
        end
        -- Dalmond and Kyndri in Auberdine. Both sell water, but the goods differ.
        assert(sells(4182,2515) and items[2515][1]=='arrows' and items[2515][2]=='Sharp Arrow')
        assert(sells(4182,2519) and items[2519][1]=='bullets' and items[2519][3]==132384)
        assert(sells(4182,4496) and items[4496][1]=='bags')
        assert(sells(4182,4470) and items[4470][1]=='supplies')
        assert(sells(4190,4542) and items[4542][1]=='food' and items[4542][2]=='Moist Cornbread')
        assert(sells(4190,1205) and items[1205][1]=='drink' and items[1205][2]=='Melon Juice')
        assert(sells(4190,159) and sells(4182,159) and not sells(4190,2515))
        assert(sells(10216,6256) and items[6256][1]=='fishing','Gubber Blump sells fishing poles, not combat weapons')
        assert(sells(6301,6529) and items[6529][1]=='fishing','Shiny Bauble is fishing tackle')
        assert(sells(6301,2901) and items[2901][1]=='supplies','Mining Picks are trade tools')
        assert(not sells(295,21815),'conditional stock slipped through')
        local vendors,itemsSeen={},{}
        for _,zone in pairs(A.ServiceDirectory) do
            for _,row in ipairs(zone) do if row.category=='vendor' then vendors[row.id]=true end end
        end
        local count,sellers=0,0
        for npc,list in pairs(stock) do
            assert(vendors[npc] and #list>0);sellers=sellers+1
            local previous=0
            for _,id in ipairs(list) do
                assert(id>previous and items[id]);itemsSeen[id]=true;previous=id;count=count+1
            end
        end
        local distinct,types=0,{}
        for id,item in pairs(items) do
            assert(itemsSeen[id] and type(item[2])=='string' and #item[2]>0 and item[3]>0)
            types[item[1]]=true;distinct=distinct+1
        end
        for _,k in ipairs({'arrows','bullets','food','drink','bags','supplies','reagents',
            'equipment','recipes','consumables','other','pets','mounts','fishing'}) do assert(types[k]) end
        assert(sellers==892 and distinct==1485 and count==12418)
        """)


if __name__=='__main__':
    unittest.main()
