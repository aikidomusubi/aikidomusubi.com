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
for d in "${DESTS[@]}"; do
  mkdir -p "$d/mockups"
  for f in docs/mockups/*.html; do cp "$f" "$d/mockups/"; done
  # the map styles and their samples, which maps.html and maps-render.html read
  cp -R docs/mockups/maps docs/mockups/venuepics docs/mockups/plans "$d/mockups/"
done
echo "→ http://localhost:4000/mockups/  ($(ls "${DESTS[0]}/mockups" | wc -l | tr -d ' ') files in ${DESTS[*]})"
