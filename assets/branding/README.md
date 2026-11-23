# Supplied Mapperly branding

Source: the user's WoW_Forever_Logo_Pack.zip, Mapperly folder, supplied 23 November 2026. These are the replacement artwork files, preserved byte-for-byte.

- Main 850x850: Media/Logo.png, full wordmark for README/project presentation.
- Icon 32x32: Media/Icon32.tga, addon-list icon referenced by the TOC.
- Icon 64x64: Media/Icon.tga, larger simple icon available for integrations.
- Small 128x128: Media/Portrait.tga, M badge used in map and full-size dialog portraits.
- Small 100x100: retained as a supplied web/display variant; the game uses the power-of-two 128px version.

Run `python tools/build_logo.py` to regenerate. Conversion preserves RGBA pixels, with no repainting, background replacement, cropping or upscaling. Existing portrait masks and placement remain in the UI code.
