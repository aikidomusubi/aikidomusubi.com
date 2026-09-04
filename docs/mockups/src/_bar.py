# -*- coding: utf-8 -*-
"""Shared chrome for the four sticky-bar proposals.

The question these mockups answer is not "what should the glossary look like"
— that was settled by `glosario-a.html` and built. It is narrower: the control
bar on /glosario/ and /recursos/ is unusable on a phone, and there are two
plausible ways out of it.

THE MEASUREMENTS ARE REAL, taken from the built pages in a 375x667 viewport
with the nav in its shrunken state:

    /glosario/   bar 389px of a 667px viewport   58%   12 chips over 5 rows
    /recursos/   bar 274px of a 667px viewport   41%    7 chips over 4 rows

Add the 49px shrunken nav above it and two thirds of a small phone is
furniture before a single entry is read. That is the whole brief.
"""

# The site's own tokens, so the proposals are the site and not a sketch.
TOKENS = """
:root{
  --ink:#111314; --mute:#5c6a70; --line:rgba(17,19,20,.13);
  --hair:rgba(17,19,20,.08); --acc:#FFF200; --blue:#064F6E;
  --paper:#fff; --tint:rgba(17,19,20,.03);
}
*{box-sizing:border-box}
html,body{margin:0;background:#f2f2f0;color:var(--ink);
  font-family:'Noto Sans',system-ui,-apple-system,sans-serif;
  -webkit-font-smoothing:antialiased}
h1,h2,h3,.fut{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-weight:400;
  letter-spacing:.04em;margin:0}
p{margin:0}
.jp{font-family:'Hiragino Sans','Noto Sans JP','Yu Gothic',sans-serif}

/* ---- the page around the prototype ------------------------------------ */
.pg{max-width:1180px;margin:0 auto;padding:3rem 2rem 5rem}
.pg > header{margin-bottom:2.5rem;max-width:46rem}
.pg h1{font-size:2.1rem;text-transform:uppercase}
.kicker{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.62rem;
  letter-spacing:.2em;text-transform:uppercase;color:var(--mute);margin-bottom:.7rem}
.lede{margin-top:1rem;font-size:1rem;line-height:1.7;color:#2c3437}
.cols{display:grid;grid-template-columns:375px minmax(0,1fr);gap:3rem;align-items:start}
@media(max-width:900px){.cols{grid-template-columns:1fr}}
.notes h2{font-size:.72rem;letter-spacing:.18em;text-transform:uppercase;
  color:var(--mute);margin:0 0 .8rem;padding-bottom:.5rem;border-bottom:2px solid var(--ink)}
.notes section{margin-bottom:2.2rem}
.notes p{font-size:.9rem;line-height:1.75;color:#2c3437;margin-bottom:.7rem}
.notes ul{margin:.2rem 0 0;padding-left:0;list-style:none}
.notes li{display:flex;gap:.5rem;font-size:.9rem;line-height:1.7;color:#2c3437;
  margin-bottom:.35rem}
.notes li > span:first-child{flex:none;width:1rem}
.fig{display:flex;gap:2.5rem;margin:.4rem 0 1rem;padding:1rem 0;
  border-top:1px solid var(--hair);border-bottom:1px solid var(--hair)}
.fig div{min-width:0}
.fig b{display:block;font-family:Futura,'Trebuchet MS',Arial,sans-serif;
  font-size:1.75rem;line-height:1;font-variant-numeric:tabular-nums}
.fig span{display:block;margin-top:.35rem;font-size:.66rem;letter-spacing:.12em;
  text-transform:uppercase;color:var(--mute)}
.fig .down b{color:#1A7444}
.tick{color:#1A7444}.cross{color:#A62C37}

/* ---- the phone -------------------------------------------------------- */
.phone{width:375px;height:667px;overflow-y:auto;overflow-x:hidden;position:relative;
  background:var(--paper);border:10px solid #111314;border-radius:26px;
  box-shadow:0 18px 40px rgba(0,0,0,.18);scrollbar-width:thin}
.phone-cap{margin-top:.8rem;font-size:.66rem;letter-spacing:.12em;
  text-transform:uppercase;color:var(--mute);text-align:center}
.stick-wrap{position:sticky;top:0;z-index:9}
.mnav{height:49px;background:#111314;color:#fff;display:flex;align-items:center;
  justify-content:space-between;padding:0 1rem}
.mnav b{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:1.05rem;
  letter-spacing:.08em}
.mnav i{display:block;width:22px;height:2px;background:#fff;
  box-shadow:0 6px 0 #fff,0 -6px 0 #fff;font-style:normal}
.head{padding:1.6rem 1rem .9rem}
.head h2{font-size:1.5rem;text-transform:uppercase;letter-spacing:.05em}
.head p{margin-top:.5rem;font-size:.82rem;line-height:1.6;color:var(--mute)}

/* ---- the list --------------------------------------------------------- */
.grp{padding:0 1rem;margin-bottom:1.8rem}
.grp[hidden]{display:none}
.gh{display:flex;align-items:baseline;gap:.6rem;padding-bottom:.5rem;
  border-bottom:2px solid var(--ink);margin-bottom:.2rem}
.gh h3{font-size:.92rem;text-transform:uppercase;letter-spacing:.09em}
.gh span{font-size:.7rem;color:var(--mute)}
.t{display:grid;gap:.1rem;padding:.7rem 0;border-bottom:1px solid var(--line)}
.t[hidden]{display:none}
.t .k{font-size:1rem;line-height:1.3}
.t .r{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.86rem}
.t .d{font-size:.78rem;line-height:1.6;color:var(--mute)}
.t .kind{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.55rem;
  letter-spacing:.16em;text-transform:uppercase;color:var(--blue)}
.empty{padding:2.5rem 1rem;font-size:.85rem;color:var(--mute)}
.empty[hidden]{display:none}
.tail{padding:2.5rem 1rem 3rem;background:#111314;color:#8b9296;font-size:.7rem}
"""


def page(title, kicker, h1, lede, phone, notes, extra_css="", js=""):
    return """<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s</title>
<link rel="stylesheet" href="/styles/all.min.css">
<style>%s
%s</style></head><body>
<div class="pg">
  <header>
    <p class="kicker">%s</p>
    <h1>%s</h1>
    <p class="lede">%s</p>
  </header>
  <div class="cols">
    <div>
      <div class="phone">%s</div>
      <p class="phone-cap">375 &times; 667 &middot; desplázalo</p>
    </div>
    <div class="notes">%s</div>
  </div>
</div>
%s
</body></html>""" % (title, TOKENS, extra_css, kicker, h1, lede, phone, notes, js)
