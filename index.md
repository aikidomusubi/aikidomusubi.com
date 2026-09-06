---
layout: default
title:
lang: es
i18n-ref: index-8oGCaMDs
# /home was the front page of the site before 2020 and Googlebot was still
# asking for it on 24 August 2026, getting a 404. It has a real equivalent —
# this page — so it redirects rather than dying. This is what redirect_from is
# for; contrast the thirty-six asset-directory entries deleted from the 404
# pages, which pointed at nothing anybody had ever linked to.
redirect_from:
  - /home
last_modified: 2026-09-06
---

{% include stickyBar.html %}

{% include home.html %}
