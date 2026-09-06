#!/bin/zsh
# Render every approved mockup into _site/mockups/ so it can be viewed at
# http://localhost:4000/mockups/…
#
# _site is wiped by `npx gulp build`; docs/mockups is not. Run this after a
# build to get the mockups back.
cd "$(dirname "$0")/../.." || exit 1
[[ -d _site ]] || { echo "no _site — run \`npx gulp build\` first"; exit 1; }
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
for f in docs/mockups/*.html; do cp "$f" _site/mockups/; done
# the map styles and their samples, which maps.html and maps-render.html read
cp -R docs/mockups/maps docs/mockups/venuepics docs/mockups/plans _site/mockups/
echo "→ http://localhost:4000/mockups/  ($(ls _site/mockups | wc -l | tr -d ' ') files)"
