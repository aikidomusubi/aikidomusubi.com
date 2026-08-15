# Japanese font sources

Full, unsubset Noto Sans JP (400, 700) and M PLUS 1p (900), kept here so
`tools/subset-ja-fonts.py` can be re-run without re-downloading them.

These are **inputs, not shipped assets** — `_config.yml` excludes this
directory from the build. What ships is the subset output in `/fonts/`.

Both are SIL Open Font License. Re-fetch from google-webfonts-helper if ever
needed:

    https://gwfh.mranftl.com/api/fonts/noto-sans-jp?subsets=japanese
    https://gwfh.mranftl.com/api/fonts/m-plus-1p?subsets=japanese
