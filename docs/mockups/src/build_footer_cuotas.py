#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Where the membership's standing links go: three options, on the real page.

The links are the members area, the membership terms and the withdrawal
function (which the EU wants reachable from every page, Directive 2023/2673),
plus signing up. They were appended to the footer's "Practicar" column on the
membership branch, which made that column a list of two different things.

Each option is the built /cuotas/ page with its footer (and, for C, the top
utility bar) rewritten, so what is judged is the site's own CSS, not a drawing
of it. Needs the dev server's build of the membership branch in _dev/.

    python3 docs/mockups/src/build_footer_cuotas.py
    ./docs/mockups/render.sh        # then open localhost:4000/mockups/footer-cuotas-a.html

  A  a fourth link column, "Tu cuota"
  B  inside "Practicar", as its own small group under a subheading
  C  split by job: "Área de miembros" in the top bar, where an account link is
     looked for; the contract's two links in a line closing the footer
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..', '..')
SRC = os.path.join(ROOT, '_dev', 'cuotas', 'index.html')
OUT = os.path.join(HERE, '..')

if not os.path.exists(SRC):
    sys.exit('needs _dev/cuotas/index.html: run `bin/dev start` on the membership-signup branch first')

PAGE = open(SRC, encoding='utf-8').read()

LINKS = [('/inscripcion/', 'Inscribirse en línea'), ('/miembros/', 'Área de miembros'),
         ('/condiciones-de-la-cuota/', 'Condiciones de la cuota'), ('/desistimiento/', 'Desistir del contrato')]
lis = lambda links: ''.join(f'<li><a href="{u}">{t}</a></li>' for u, t in links)

# The branch's current state: three extra links at the end of Practicar. Every
# option starts from Practicar without them.
def strip_extras(html):
    for u in ('/miembros/', '/condiciones-de-la-cuota/', '/desistimiento/'):
        html = re.sub(rf'\s*<li><a href="{re.escape(u)}">[^<]*</a></li>', '', html, count=1)
    return html

BASE = strip_extras(PAGE)
PRACTICAR = re.search(r'<nav class="ft-col" aria-labelledby="ft-h-classes">.*?</nav>', BASE, re.S).group(0)

BANNER_CSS = """
.mk-banner{position:relative;z-index:2000;background:#FFF200;color:#111314;font:14px/1.45 "Noto Sans",Arial,sans-serif;padding:.7rem 1.2rem}
.mk-banner b{font-family:Futura,"Trebuchet MS",Arial,sans-serif;letter-spacing:.04em;text-transform:uppercase;margin-right:.6rem}
.mk-banner a{color:#111314;margin-left:.8rem}
"""


def page(letter, title, note, html, css):
    others = ''.join(f'<a href="footer-cuotas-{x}.html">Opción {x.upper()}</a>' for x in 'abc' if x != letter)
    banner = f'<div class="mk-banner" role="note"><b>Opción {letter.upper()} · {title}</b>{note}{others}</div>'
    html = html.replace('<body', '<body data-mockup="footer"', 1)
    html = re.sub(r'(<body[^>]*>)', r'\1' + banner, html, count=1)
    html = html.replace('</head>', f'<style>{BANNER_CSS}{css}</style></head>', 1)
    html = html.replace('<title>', f'<title>Footer {letter.upper()} · ', 1)
    path = os.path.join(OUT, f'footer-cuotas-{letter}.html')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print('  docs/mockups/' + os.path.basename(path))


# ---------------------------------------------------------------------------
# A: a fourth link column. Five blocks at desktop; at tablet the identity row
# stays, and the four lists share the row below.
col_a = (f'<nav class="ft-col" aria-labelledby="ft-h-cuota"><h2 class="ft-colh" id="ft-h-cuota">Tu cuota</h2>'
         f'<ul>{lis(LINKS)}</ul></nav>')
A = BASE.replace(PRACTICAR, PRACTICAR + col_a, 1)
CSS_A = """
@media (min-width:576px){ .ft-grid{grid-template-columns:repeat(4,1fr)} .ft-grid>.ft-id{grid-column:1 / span 2} }
@media (min-width:992px){ .ft-grid{grid-template-columns:1.35fr 1fr 1fr 1.05fr 1.15fr;gap:2.2rem} .ft-grid>.ft-id{grid-column:auto} }
"""
page('a', 'Una columna más: «Tu cuota»',
     'Cuatro enlaces en su propia columna, entre «Practicar» y «Sobre nosotros». «Practicar» vuelve a ser solo el menú.', A, CSS_A)

# B: inside Practicar, as its own group with a subheading.
prac_b = PRACTICAR.replace('</ul>\n            </nav>', '</ul>\n            </nav>', 1)
group_b = f'<h3 class="ft-subh">Tu cuota</h3><ul class="ft-sub">{lis(LINKS)}</ul>'
prac_b = re.sub(r'(</ul>)(\s*</nav>)$', r'\1' + group_b + r'\2', PRACTICAR, count=1)
B = BASE.replace(PRACTICAR, prac_b, 1)
CSS_B = """
.ft-subh{font-family:Futura,"Trebuchet MS",Arial,sans-serif;font-size:.74rem;font-weight:400;letter-spacing:.16em;text-transform:uppercase;
  color:#969798;margin:1.4rem 0 .8rem;padding-top:1.1rem;border-top:1px solid rgba(255,255,255,.14)}
"""
page('b', 'Dentro de «Practicar», como grupo aparte',
     'Sin columna nueva: los enlaces de la cuota van al final de «Practicar», separados por una raya y su propio título.', B, CSS_B)

# C: split by job. The members area goes in the top utility bar, beside the
# email and the languages; the two contract links close the footer body.
C = BASE.replace('<a class="nv-mail"', '<a class="nv-member" href="/miembros/">Área de miembros</a><a class="nv-mail"', 1)
row = ('<div class="ft-contract"><span class="ft-contract-h">La cuota</span><ul>'
       + lis([LINKS[0], LINKS[2], LINKS[3]]) + '</ul></div>')
# After the grid closes and before the footer body does: the last list's
# </nav>, then the grid's </div>.
C = re.sub(r'(</nav>\s*</div>)(\s*</div>\s*<div class="ft-strip">)', lambda m: m.group(1) + row + m.group(2), C, count=1)
assert 'ft-contract' in C
CSS_C = """
.nv-member{color:#FFF200 !important;font-weight:700;text-decoration:none;margin-right:1.4rem;font-size:.72rem}
.nv-member:hover{text-decoration:underline}
.ft-contract{display:flex;flex-wrap:wrap;align-items:baseline;gap:.4rem 1.6rem;margin-top:2.2rem;padding-top:1.1rem;padding-bottom:.4rem;
  border-top:1px solid rgba(255,255,255,.14)}
.ft-contract-h{font-family:Futura,"Trebuchet MS",Arial,sans-serif;font-size:.74rem;letter-spacing:.16em;text-transform:uppercase;color:#969798}
.ft-contract ul{display:flex;flex-wrap:wrap;gap:.4rem 1.6rem;margin:0;padding:0;list-style:none}
.ft-contract a{color:#A5A5A6;font-size:.84rem;text-decoration:none}
.ft-contract a:hover{color:#fff;text-decoration:underline}
"""
page('c', 'Repartidos según para qué sirven',
     '«Área de miembros» arriba, junto al correo y los idiomas, donde se busca el acceso a la cuenta. Inscribirse, condiciones y desistir, en una línea que cierra el pie.',
     C, CSS_C)
