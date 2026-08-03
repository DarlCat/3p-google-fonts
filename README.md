# 3p-google-fonts

Google fonts for viewer use:

- **Inter** (variable) - primary UI sans
- **Noto Sans Symbols 2** (subset) - symbol fallback for blocks listed in
  `Noto_Sans_Symbols_2/unicode-blocks.txt`

All fonts are under the SIL Open Font License 1.1.

## Extending symbol coverage

Sources live under `Noto_Sans_Symbols_2/` (upstream **hinted** TTF + block list).
The subset is generated into `stage/fonts/` at package build time, same as Inter.

1. Edit `Noto_Sans_Symbols_2/unicode-blocks.txt` (`NAME START END` per range).
2. Rebuild the package (`fonttools` required: `pip install fonttools`).
3. Commit the blocks file (and the hinted TTF only if you upgrade upstream).
