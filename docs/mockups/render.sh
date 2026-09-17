#!/bin/zsh
# Render every approved mockup into _site/mockups/ so it can be viewed at
# http://localhost:4000/mockups/…
#
# _site is wiped by `npx gulp build`; docs/mockups is not. Run this after a
# build to get the mockups back.
cd "$(dirname "$0")/../.." || exit 1

# WHERE THEY GO depends on what is serving. The dev server's destination is
# `_dev` now (bin/dev), and `_site` is the build's alone — so rendering only
# into `_site` would put them somewhere nothing is listening. Both get a copy
# when both exist, which costs a few hundred kilobytes of throwaway HTML and
# means the link below is always live.
DESTS=()
[[ -d _dev  ]] && DESTS+=(_dev)
[[ -d _site ]] && DESTS+=(_site)
if [[ ${#DESTS[@]} -eq 0 ]]; then
  echo "nothing built — run \`bin/dev start\` or \`npx gulp build\` first"; exit 1
fi
mkdir -p _site/mockups
python3 docs/mockups/src/build3.py
python3 docs/mockups/src/build_gloss.py
python3 docs/mockups/src/build_about.py
python3 docs/mockups/src/build_extra.py
python3 docs/mockups/src/build_res.py
python3 docs/mockups/src/build_ura_res.py
python3 docs/mockups/src/build_ura_arch.py
python3 docs/mockups/src/build_shidoin.py
python3 docs/mockups/src/build_bar.py
python3 docs/mockups/src/build_loc.py
python3 docs/mockups/src/build_maps.py
python3 docs/mockups/src/build_maps_gl.py
python3 docs/mockups/src/build_venuepics.py
python3 docs/mockups/src/build_plans.py
python3 docs/mockups/src/build_poster.py
python3 docs/mockups/src/build_firstclass.py
python3 docs/mockups/src/build_links.py
for d in "${DESTS[@]}"; do
  mkdir -p "$d/mockups"
  for f in docs/mockups/*.html; do cp "$f" "$d/mockups/"; done
  # the map styles and their samples, which maps.html and maps-render.html read
  cp -R docs/mockups/maps docs/mockups/venuepics docs/mockups/plans "$d/mockups/"
done
# ZSH ARRAYS ARE 1-INDEXED. This line read `${DESTS[0]}`, which is empty in zsh
# — so it ran `ls /mockups`, printed "No such file or directory" and reported
# "0 files" every single time, on a run that had just copied 57 of them
# correctly. The copy above was never broken; only the report of it was.
# Counting per destination inside a loop avoids the subscript altogether and
# says more besides.
for d in "${DESTS[@]}"; do
  echo "  $d/mockups  $(ls "$d/mockups"/*.html | wc -l | tr -d ' ') pages"
done
echo "→ http://localhost:4000/mockups/"
