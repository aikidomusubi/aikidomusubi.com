#!/bin/zsh
# shot.sh <url> <out.png> [w] [h]
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
W=${3:-1440}; H=${4:-9000}
D=$(mktemp -d)
"$CH" --headless --disable-gpu --hide-scrollbars --no-first-run --user-data-dir="$D" \
  --window-size=$W,$H --virtual-time-budget=9000 --screenshot="$2" "$1" 2>/dev/null
rm -rf "$D"
sips -g pixelHeight -g pixelWidth "$2" 2>/dev/null | tail -2
