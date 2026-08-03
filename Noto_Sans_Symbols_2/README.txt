Noto Sans Symbols 2 (subset)
============================

Source: https://github.com/notofonts/symbols
Release: NotoSansSymbols2-v2.008
Upstream path: hinted/ttf/NotoSansSymbols2-Regular.ttf

Note: the release also has full/ and googlefonts/ TTFs (~1.2 MB) with extra
Latin/punctuation. We use the hinted build (~656 KB) as the subset input;
symbol coverage for our blocks is the same.

We package a *subset* of Noto Sans Symbols 2 so the viewer package size does not bloat.
Only the Unicode blocks listed in unicode-blocks.txt are included in our output package.

Files
---------------------------------------------
  NotoSansSymbols2-Regular-hinted.ttf  Upstream hinted build (subset input)
  unicode-blocks.txt                   Ranges to keep
  subset_symbols.py                    Build-time subsetter
  OFL.txt                              SIL Open Font License 1.1

Adding more Unicode blocks
--------------------------
1. Append a line to unicode-blocks.txt:
     Block_Name  START  END

   Example (Miscellaneous Symbols and Arrows):
     Misc_Symbols_And_Arrows  2B00  2BFF

2. Rebuild the package (or dry-run the subsetter into /tmp):
     python3 Noto_Sans_Symbols_2/subset_symbols.py \
       --output /tmp/NotoSansSymbols2-Regular.ttf

   Requires: pip install fonttools

Bumping upstream release
------------------------
1. Download the newer release from upstream
     Extracted filepath Example
       /NotoSansSymbols2-v2.008/NotoSansSymbols2/hinted/ttf/NotoSansSymbols2-Regular.ttf

2. Copy and rename the hinted Regular TTF file to 
     ./Noto_Sans_Symbols_2/NotoSansSymbols2-Regular-hinted.ttf

License
-------
SIL Open Font License, Version 1.1 (see OFL.txt)
