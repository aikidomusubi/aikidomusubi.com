#!/bin/bash
# Starts Jekyll serve and Gulp watch in a Hyper split pane.
# Uses clipboard paste instead of keystroke-per-character for reliability.
# Idempotent — does nothing if both processes are already running.
PROJECT="/Applications/MAMP/htdocs/aikidomusubi.com"

/usr/bin/pgrep -f "jekyll serve" > /dev/null 2>&1 && \
/usr/bin/pgrep -f "gulp watch"   > /dev/null 2>&1 && exit 0

# RUBYOPT: the shell has an empty LANG, so without this the Sass converter
#   treats files as US-ASCII and the build dies on non-ASCII characters.
# --config: _config_dev.yml overrides site.url to localhost, otherwise the
#   locally served pages load their CSS/JS/images from the live site.
JEKYLL_CMD="cd '$PROJECT' && RUBYOPT='-E utf-8:utf-8' bundle exec jekyll serve --config _config.yml,_config_dev.yml"
GULP_CMD="cd '$PROJECT' && npx gulp watch"

osascript << APPLESCRIPT
set the clipboard to "$JEKYLL_CMD"

tell application "Hyper" to activate
delay 2

tell application "System Events"
    tell process "Hyper"
        keystroke "n" using {command down}
        delay 3
        keystroke "v" using {command down}
        delay 0.3
        keystroke return
        delay 1
        keystroke "d" using {command down}
        delay 3
    end tell
end tell

set the clipboard to "$GULP_CMD"

tell application "System Events"
    tell process "Hyper"
        keystroke "v" using {command down}
        delay 0.3
        keystroke return
    end tell
end tell
APPLESCRIPT
