# -*- coding: utf-8 -*-
"""Two proposals for the instructors-in-training programme.

  B  a section on /clases/, after the four disciplines
  C  a card on /clases/ that opens the full document as a panel on /recursos/

Same copy in both, so the comparison is about where it lives and how much of it
you get at once — not about the writing.

The Tuesday 20:30 slot already exists in _data/schedule.yml with
`instructor: trainee`, and the timetable already prints "Instructor en
formación" on it. Nothing on the site says what that means; that is the gap
both of these fill, and it is why /clases/ is the page in both.

Writes into _site/mockups/, which `npx gulp build` wipes. The source lives in
docs/ and is in git; see docs/mockups/README.md.
"""
import os

ROOT = '/Applications/MAMP/htdocs/aikidomusubi.com'
OUT = os.path.join(ROOT, '_site', 'mockups')
DOCS = os.path.join(ROOT, 'docs', 'mockups')

# --- the copy, shared -------------------------------------------------------
FACTS = [('2 años', 'de programa'), ('4 plazas', 'por promoción'),
         ('Martes', '20:30 – 21:30'), ('Abierto', 'a otros dojos Aikikai')]

LEDE = ('Los martes a las 20:30 la clase la da alguien que está aprendiendo a darla.')

BODY = (
    'Un dojo dura lo que duran sus profesores. Enseñar aikido no se sigue de '
    'saber hacerlo: son dos cosas distintas, y la segunda se aprende como se '
    'aprende la primera —en el tatami, delante de gente, con alguien mirando.')

PARTS = [
    ('El programa',
     ['Cada martes de 20:30 a 21:30 la clase la dirige un yūdansha en '
      'formación. El director técnico está en el tatami, practicando como uno '
      'más, y comenta después: qué se ha entendido, qué no, y por qué.',
      'No es una clase de prueba ni una suplencia. Es la clase de ese día, con '
      'sus alumnos, su programa y sus consecuencias.']),
    ('Los dos años',
     ['El primer año se observa y se asiste: preparar la sesión, corregir en '
      'pareja, llevar el calentamiento, tomar el examen de otro.',
      'El segundo se dirige. La frecuencia sube y el comentario baja, hasta '
      'que la clase se sostiene sola.',
      'Dos años no es una cifra ritual: es lo que tarda alguien en pasar por '
      'un curso entero de programa, dos ciclos de exámenes y un verano.']),
    ('Qué se espera',
     ['Grado de yūdansha y práctica regular, aquí o en el dojo de origen.',
      'Asistencia sostenida: enseñar los martes exige entrenar el resto de la '
      'semana.',
      'Disposición a que te corrijan delante de la clase, que es la parte '
      'incómoda y la que enseña.']),
    ('Para quién',
     ['Para nuestros yūdansha, y para los de cualquier dojo Aikikai que quiera '
      'formar a alguien y no tenga dónde. Se viene con el consentimiento del '
      'propio sensei, y lo aprendido vuelve al dojo de origen.',
      'Cuatro plazas. No es una cifra de marketing: son las que caben en una '
      'hora semanal si cada uno ha de dirigir con regularidad.']),
]

BASE = """
:root{--ink:#111314;--mute:#4f5c62;--line:rgba(17,19,20,.13);--rule:rgba(17,19,20,.30);
      --acc:#FFF200;--olive:#6B7140;--green:#1A7444;--panel:#f6f7f7}
html,body{margin:0;background:#fff;color:var(--ink);
  font-family:'Noto Sans',system-ui,sans-serif;-webkit-font-smoothing:antialiased;line-height:1.7}
*{box-sizing:border-box}
h1,h2,h3,h4{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-weight:400;margin:0;letter-spacing:.04em}
p{margin:0}
a{color:inherit}
.w{max-width:1140px;margin:0 auto;padding-left:6rem;padding-right:6rem}
@media(max-width:991.98px){.w{padding-left:4rem;padding-right:4rem}}
@media(max-width:767.98px){.w{padding-left:2rem;padding-right:2rem}}
.badge{position:fixed;top:0;left:0;z-index:99;background:var(--acc);color:#111314;
  font-family:Futura,sans-serif;font-size:.6rem;letter-spacing:.18em;text-transform:uppercase;padding:.5rem .9rem}
.top{padding:3.4rem 0 0;text-align:center}
.top h1{font-size:2rem;letter-spacing:1px;text-transform:uppercase;margin:2rem 0}
.top .lede{font-size:.9rem;color:var(--mute);margin:0 0 3.4rem}

/* a stand-in for the four discipline blocks already on /clases/ */
.disc{display:grid;grid-template-columns:repeat(2,1fr);gap:1px;background:var(--line);
  border-top:1px solid var(--line);border-bottom:1px solid var(--line);margin-bottom:4rem}
.disc div{background:#fff;padding:1.4rem 1.2rem;min-height:6.5rem}
.disc b{font-family:Futura,sans-serif;font-weight:400;font-size:.95rem;display:block}
.disc span{font-size:.76rem;color:var(--mute)}
.ghost{color:#9aa2a5;font-size:.7rem;letter-spacing:.14em;text-transform:uppercase;
  text-align:center;padding:.8rem 0 2.4rem}
footer.end{margin-top:3.4rem;padding:2.4rem 0 4rem;border-top:1px solid var(--line);
  font-size:.82rem;color:var(--mute)}
footer.end b{color:var(--ink);font-weight:400}
.cost{margin-top:.8rem;font-family:ui-monospace,Menlo,monospace;font-size:.72rem;color:var(--olive)}
"""


def page(title, badge, body, note, cost, extra=''):
    return """<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s</title><link rel="stylesheet" href="/styles/all.min.css">
<style>%s%s</style></head><body>
<div class="badge">%s</div>
<div class="w top"><h1>Clases</h1>
<p class="lede">Aikido, iaijutsu, judo y karate. Cuatro disciplinas, un tatami.</p></div>
<div class="w"><div class="disc">
  <div><b>Aikido</b><span>合気道 · todos los niveles, principiantes y armas</span></div>
  <div><b>Iaijutsu</b><span>居合術 · el corte, con el sable</span></div>
  <div><b>Judo</b><span>柔道 · de pie y en el suelo</span></div>
  <div><b>Karate</b><span>空手 · shōtōkan</span></div>
</div></div>
<p class="ghost">— las cuatro disciplinas, tal como están hoy —</p>
%s
<div class="w"><footer class="end">%s<p class="cost">%s</p></footer></div>
</body></html>""" % (title, BASE, extra, badge, body, note, cost)


# ---------------------------------------------------------------------------
# B · a section on the Classes page
# ---------------------------------------------------------------------------
B_CSS = """
.sh{background:#111314;color:#fff;padding:4rem 0;margin:0 0 1rem}
.sh .w{display:grid;grid-template-columns:1.35fr 1fr;gap:4rem;align-items:start}
@media(max-width:900px){.sh .w{grid-template-columns:1fr;gap:2.4rem}}
.sh .eyebrow{font-family:Futura,sans-serif;font-size:.6rem;letter-spacing:.24em;
  text-transform:uppercase;color:var(--acc);margin:0 0 1rem}
.sh h2{font-size:1.9rem;color:#fff;margin:0 0 1.2rem;line-height:1.15}
.sh .lede{font-size:1.05rem;color:#fff;margin:0 0 1.2rem}
.sh p.body{font-size:.92rem;color:#c9d0d3;margin:0 0 1rem}
.sh .facts{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:rgba(255,255,255,.16);
  border:1px solid rgba(255,255,255,.16)}
.sh .facts div{background:#111314;padding:1rem 1.1rem}
.sh .facts b{display:block;font-family:Futura,sans-serif;font-size:1.15rem;color:#fff;line-height:1.1}
.sh .facts span{display:block;margin-top:.3rem;font-size:.7rem;letter-spacing:.1em;
  text-transform:uppercase;color:#9aa2a5}
.sh .parts{margin-top:2.4rem;display:grid;grid-template-columns:repeat(2,1fr);gap:1.8rem 3rem}
@media(max-width:900px){.sh .parts{grid-template-columns:1fr}}
.sh .parts h3{font-size:.66rem;letter-spacing:.18em;text-transform:uppercase;color:var(--acc);
  margin:0 0 .5rem;padding-bottom:.3rem;border-bottom:1px solid rgba(255,255,255,.2)}
.sh .parts p{font-size:.84rem;color:#c9d0d3;margin:0 0 .5rem}
.sh .cta{margin-top:2.4rem;display:inline-flex;gap:.5rem;align-items:center;
  background:var(--acc);color:#111314;padding:.7rem 1.2rem;font-family:Futura,sans-serif;
  font-size:.8rem;letter-spacing:.06em;text-decoration:none}
.sh .tt{margin-top:1.2rem;font-size:.78rem;color:#9aa2a5}
.sh .tt b{color:#fff;font-weight:400}
"""


def build_b():
    facts = ''.join('<div><b>%s</b><span>%s</span></div>' % f for f in FACTS)
    parts = ''.join('<div><h3>%s</h3>%s</div>' % (h, ''.join('<p>%s</p>' % p for p in ps))
                    for h, ps in PARTS)
    body = """
<section class="sh"><div class="w">
  <div>
    <p class="eyebrow">Instructores en formación · 指導者研修</p>
    <h2>Enseñar también se aprende</h2>
    <p class="lede">%s</p>
    <p class="body">%s</p>
    <p class="tt">En el horario ese hueco ya aparece: <b>martes, 20:30 — Instructor en formación</b>.</p>
    <a class="cta" href="#">Escríbenos &rarr;</a>
  </div>
  <div class="facts">%s</div>
  <div style="grid-column:1/-1"><div class="parts">%s</div></div>
</div></section>""" % (LEDE, BODY, facts, parts)
    return page('Clases · propuesta B', 'Propuesta B · sección en Clases', body,
                '<b>Propuesta B.</b> Todo el programa vive en /clases/, en una banda oscura que '
                'lo separa de las cuatro disciplinas sin sacarlo de la página. Quien mira el '
                'horario y ve «Instructor en formación» encuentra la respuesta sin ir a ningún '
                'sitio. El precio es que no tiene URL propia: no se puede enviar el enlace a un '
                'yūdansha de otro dojo sin mandarle a la página de clases entera.',
                'coste: un bloque en _data/classes.yml · sin URL nueva · sin entrada de menú',
                B_CSS)


# ---------------------------------------------------------------------------
# C · a card on Classes, the document in the panel
# ---------------------------------------------------------------------------
C_CSS = """
.card{border:1px solid var(--rule);padding:1.8rem 2rem;display:grid;
  grid-template-columns:1fr auto;gap:2rem;align-items:center;margin:0 0 1rem}
@media(max-width:760px){.card{grid-template-columns:1fr;gap:1.2rem}}
.card .eyebrow{font-family:Futura,sans-serif;font-size:.58rem;letter-spacing:.22em;
  text-transform:uppercase;color:var(--olive);margin:0 0 .6rem}
.card h2{font-size:1.35rem;margin:0 0 .5rem}
.card p{font-size:.9rem;color:var(--mute);margin:0 0 .6rem}
.card .meta{font-size:.74rem;color:var(--mute);letter-spacing:.04em}
.card .meta b{color:var(--ink);font-weight:400}
.card .go{display:inline-flex;align-items:center;gap:.5rem;background:#111314;color:#fff;
  padding:.7rem 1.2rem;font-family:Futura,sans-serif;font-size:.8rem;text-decoration:none;
  white-space:nowrap}
/* the panel, as /recursos/ already renders one */
.stage{margin-top:3rem;border-top:1px solid var(--line);padding-top:2rem}
.stage>p{font-size:.7rem;letter-spacing:.14em;text-transform:uppercase;color:#9aa2a5;
  text-align:center;margin:0 0 1rem}
.panel{border:1px solid var(--rule);box-shadow:-1rem 0 3rem rgba(0,0,0,.10);max-width:60rem;
  margin:0 auto;background:#fff}
.pbar{display:flex;align-items:center;gap:.9rem;flex-wrap:wrap;padding:.8rem 2rem;
  border-bottom:1px solid var(--line)}
.pbar .eye{flex:0 0 100%;font-family:Futura,sans-serif;font-size:.58rem;letter-spacing:.22em;
  text-transform:uppercase;color:var(--mute)}
.pbar h3{flex:1 1 14rem;font-size:1.15rem}
.pbar .btn{font-size:.78rem;padding:.42rem .7rem;background:rgba(17,19,20,.05);border-radius:.25rem}
.pbar .btn.dark{background:#111314;color:#fff}
.pbody{padding:1.8rem 2rem 2.4rem}
.pbody .lede{font-size:.9rem;color:var(--mute);max-width:44rem;margin:0 0 1.4rem}
.pcols{columns:2;column-gap:2.8rem}
@media(max-width:820px){.pcols{columns:1}}
.pcols section{break-inside:avoid;margin:0 0 1.6rem}
.pcols h4{font-family:Futura,sans-serif;font-size:.66rem;letter-spacing:.16em;text-transform:uppercase;
  margin:0 0 .6rem;padding-bottom:.3rem;border-bottom:2px solid var(--ink)}
.pcols ol{margin:0;padding:0;list-style:none;counter-reset:r}
.pcols li{counter-increment:r;position:relative;padding-left:1.5rem;margin:0 0 .7rem;
  font-size:.86rem;line-height:1.55;color:rgba(17,19,20,.84)}
.pcols li::before{content:counter(r);position:absolute;left:0;top:.1rem;
  font-family:Futura,sans-serif;font-size:.72rem;color:rgba(17,19,20,.45)}
"""


def build_c():
    parts = ''.join('<section><h4>%s</h4><ol>%s</ol></section>'
                    % (h, ''.join('<li>%s</li>' % p for p in ps)) for h, ps in PARTS)
    body = """
<div class="w">
  <div class="card">
    <div>
      <p class="eyebrow">Instructores en formación · 指導者研修</p>
      <h2>Enseñar también se aprende</h2>
      <p>%s</p>
      <p class="meta"><b>2 años</b> · <b>4 plazas</b> · martes 20:30 · abierto a otros dojos Aikikai</p>
    </div>
    <a class="go" href="#">Leer el programa &rarr;</a>
  </div>
</div>

<div class="w stage">
  <p>— y esto es lo que abre: /recursos/?r=shidoin —</p>
  <div class="panel">
    <div class="pbar">
      <span class="eye">Etiqueta y normas</span>
      <h3>Instructores en formación</h3>
      <span class="btn">Compartir</span><span class="btn">Imprimir</span>
      <span class="btn dark">Cerrar</span>
    </div>
    <div class="pbody">
      <p class="lede">%s %s</p>
      <div class="pcols">%s</div>
    </div>
  </div>
</div>""" % (LEDE, LEDE, BODY, parts)
    return page('Clases · propuesta C', 'Propuesta C · tarjeta + panel', body,
                '<b>Propuesta C.</b> En /clases/ queda una tarjeta corta; el programa entero es '
                'un documento en el panel que ya usan el programa de examen y las normas — con '
                'compartir, imprimir y URL propia (<code>/recursos/?r=shidoin</code>). Un yūdansha '
                'de otro dojo puede enviárselo a su sensei o imprimirlo. El precio es que el '
                'detalle vive en Recursos, que es donde están los papeles, no las invitaciones.',
                'coste: una tarjeta + un documento · reutiliza el panel existente · URL propia',
                C_CSS)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for name, fn in (('shidoin-b', build_b), ('shidoin-c', build_c)):
        html = fn()
        open(os.path.join(OUT, name + '.html'), 'w', encoding='utf-8').write(html)
        open(os.path.join(DOCS, name + '.html'), 'w', encoding='utf-8').write(html)
        print('  %s.html' % name)
