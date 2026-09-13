#!/bin/bash
# Fired by the UserPromptSubmit hook in .claude/settings.local.json, so this
# runs on EVERY message. It must therefore be cheap and it must be correct
# about what is already up.
#
# It used to be neither. It drove Hyper through AppleScript — activate, open a
# tab, paste from the clipboard, press return, twice, with nine seconds of
# `delay` — and its idempotence test was an AND: it exited early only when BOTH
# processes were running, so losing either one started BOTH again. Five stacked
# processes at the worst, and a stolen keyboard focus every time.
#
# All of the work is in bin/dev now. `start --quiet` checks two pidfiles and
# returns in milliseconds when everything is already running, which is the
# normal case.
exec bash "$(dirname "$0")/../bin/dev" start --quiet
