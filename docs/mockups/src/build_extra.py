# -*- coding: utf-8 -*-
import io, os
OUT = '/Applications/MAMP/htdocs/aikidomusubi.com/_site/mockups'

SHELL = """<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s</title><link rel="stylesheet" href="/styles/all.min.css">
<style>
:root{--ink:#111314;--mute:#5c6a70;--line:rgba(17,19,20,.13);--acc:#FFF200}
html,body{margin:0;background:#fff;color:var(--ink);
  font-family:'Noto Sans',system-ui,sans-serif;-webkit-font-smoothing:antialiased}
*{box-sizing:border-box}
h1,h2,h3{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-weight:400;margin:0;
  letter-spacing:.04em}
p{margin:0}
.w{max-width:1140px;margin:0 auto;padding:0 6rem}
@media(max-width:991.98px){.w{padding:0 4rem}}
@media(max-width:767.98px){.w{padding:0 2rem}}
.top{padding:3.2rem 0 2rem}
.top h1{font-size:2.4rem;text-transform:uppercase;letter-spacing:.06em}
.top .lede{margin-top:1.1rem;max-width:44rem;font-size:1.05rem;line-height:1.75;color:#2c3437}
@media(max-width:575.98px){.top h1{font-size:1.8rem}}
%s
</style></head><body>%s</body></html>"""

# ═══════════════════════════════════════════════════════════════════════════
# Declaración de accesibilidad
# ═══════════════════════════════════════════════════════════════════════════
A11Y_CSS = """
.a-body{padding:0 0 5rem;max-width:43.25rem}
.a-body h2{font-size:1.15rem;text-transform:uppercase;letter-spacing:.09em;
  margin:2.6rem 0 .9rem;padding-top:1.4rem;border-top:1px solid var(--line)}
.a-body p{font-size:.98rem;line-height:1.85;color:#2c3437;margin-bottom:1rem}
.a-body ul{margin:0 0 1rem;padding-left:1.1rem}
.a-body li{font-size:.95rem;line-height:1.8;color:#2c3437;margin-bottom:.35rem}
.a-body a{color:var(--ink);text-decoration:underline;text-underline-offset:.18em}
.a-flag{border-left:3px solid var(--acc);background:#fffdf0;padding:1.1rem 1.3rem;
  margin:1.4rem 0 1.8rem}
.a-flag p{margin:0;font-size:.95rem;line-height:1.75}
.a-flag b{font-weight:400;font-family:Futura,'Trebuchet MS',Arial,sans-serif;
  display:block;font-size:.62rem;letter-spacing:.18em;text-transform:uppercase;
  color:#5c6a70;margin-bottom:.5rem}
.a-facts{display:grid;grid-template-columns:auto 1fr;gap:.55rem 2rem;font-size:.9rem;
  margin-top:1.6rem;padding-top:1.3rem;border-top:1px solid var(--line)}
.a-facts dt{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.62rem;
  letter-spacing:.16em;text-transform:uppercase;color:var(--mute);padding-top:.24rem}
.a-facts dd{margin:0;color:var(--ink);line-height:1.6}
@media(max-width:575.98px){.a-facts{grid-template-columns:1fr;gap:.1rem}
  .a-facts dd{margin-bottom:.8rem}}
"""

A11Y = """
<header class="top w"><h1>Declaración de accesibilidad</h1>
<p class="lede">Qué hemos hecho para que este sitio se pueda usar con teclado, con lector de
   pantalla o con la vista cansada, qué sabemos que todavía falla, y cómo avisarnos si
   encuentras algo que no funciona.</p></header>
<div class="w"><div class="a-body">

<div class="a-flag"><p><b>En resumen</b>Este sitio es <strong>parcialmente conforme</strong>
  con la norma UNE-EN 301 549 y las WCAG 2.1 en nivel AA. Parcialmente porque hay
  excepciones, y están todas listadas más abajo.</p></div>

<h2>Nuestro compromiso</h2>
<p>La Associació Cultural Musubi Aikido quiere que cualquiera pueda consultar los horarios,
   encontrar el dojo y escribirnos, con independencia de cómo navegue. No estamos obligados
   por ley a publicar esta declaración: no somos un organismo público ni prestamos servicios
   de comercio electrónico. La publicamos porque hemos hecho el trabajo y porque nos parece
   que un dojo que dice recibir a todo el mundo debería decirlo también aquí.</p>

<h2>Qué hemos hecho</h2>
<ul>
  <li>Un <strong>enlace para saltar al contenido</strong> como primer elemento de cada página,
    para no tener que tabular por los veinte enlaces del menú.</li>
  <li><strong>Contraste medido, no estimado</strong>, elemento por elemento y contra el fondo
    real. Todo el texto llega al menos a 4,5:1, y los elementos de interfaz a 3:1.</li>
  <li>Navegación completa <strong>con teclado</strong>, con foco siempre visible y submenús
    accesibles aunque JavaScript no se ejecute.</li>
  <li>Un solo <code>h1</code> por página y <strong>ningún nivel de encabezado saltado</strong>,
    verificado automáticamente en cada compilación.</li>
  <li>Texto alternativo en las imágenes que informan, y ninguno en las decorativas.</li>
  <li>Respeto por <strong>«reducir movimiento»</strong>: si tu sistema lo pide, las
    animaciones se detienen.</li>
  <li>El texto se puede <strong>ampliar al 200 %</strong> sin que se solape ni desaparezca
    nada, y ninguna página necesita desplazamiento horizontal.</li>
  <li><strong>Sin dependencias externas</strong>: tipografías y scripts se sirven desde este
    dominio, así que la página funciona igual con bloqueadores activos.</li>
  <li>El idioma de cada página está declarado, y las citas en japonés van marcadas como
    japonés para que un lector de pantalla las pronuncie bien.</li>
</ul>

<h2>Lo que sabemos que todavía falla</h2>
<ul>
  <li>Los <strong>PDF de terceros</strong> (programas de seminario, formularios de
    federaciones) no siempre están etiquetados. Si necesitas uno en otro formato, pídenoslo
    y te lo pasamos.</li>
  <li>Los <strong>planos de acceso</strong> son imágenes de satélite. Llevan descripción
    textual con la dirección y la entrada, pero la imagen en sí no es interpretable.</li>
  <li>Los <strong>vídeos alojados en Instagram</strong> no llevan subtítulos y no están bajo
    nuestro control. Estamos subtitulando los nuevos.</li>
  <li>Algunos <strong>textos antiguos</strong> traducidos hace años usan una redacción más
    enrevesada de la que nos gustaría. Los vamos reescribiendo.</li>
</ul>

<h2>Cómo avisarnos</h2>
<p>Si encuentras una barrera, escríbenos a
   <a href="mailto:info@aikidomusubi.com">info@aikidomusubi.com</a> contando qué página era y
   qué te pasó. Contestamos en un plazo de quince días. Si lo que necesitas es un contenido
   concreto en otro formato, dilo y te lo preparamos.</p>

<dl class="a-facts">
  <dt>Estado</dt><dd>Parcialmente conforme con WCAG 2.1 nivel AA</dd>
  <dt>Método</dt><dd>Autoevaluación, con comprobaciones automáticas en cada compilación y
    revisión manual de contraste, teclado y foco</dd>
  <dt>Declaración</dt><dd>23 de agosto de 2026</dd>
  <dt>Última revisión</dt><dd>23 de agosto de 2026</dd>
  <dt>Contacto</dt><dd>info@aikidomusubi.com</dd>
</dl>
</div></div>
"""

# ═══════════════════════════════════════════════════════════════════════════
# Mapa del sitio
# ═══════════════════════════════════════════════════════════════════════════
TREE = [
    ('Practicar', '#E2625E', [
        ('Clases', '/clases/', 'Las cuatro disciplinas y sus programas'),
        ('Horarios', '/horarios/', 'La semana entera, con filtros y exportación'),
        ('Cuotas', '/cuotas/', 'Qué cuesta y qué incluye'),
        ('Visitantes', '/visitantes/', 'Entrenar con nosotros de paso'),
        ('Recursos', '/recursos/', 'Guías de examen, formularios, armas'),
    ]),
    ('Sobre nosotros', '#B7C2A9', [
        ('El dojo', '/sobre-nosotros/el-dojo/', 'El espacio y cómo se cuida'),
        ('Aikido', '/sobre-nosotros/aikido/', 'Qué es y de dónde viene'),
        ('La asociación', '/sobre-nosotros/la-asociacion/', 'Quiénes somos y cómo nos organizamos'),
        ('Glosario', '/glosario/', 'Las palabras del tatami'),
    ]),
    ('Eventos', '#FBE6A0', [
        ('Seminarios', '/seminarios/', 'Los seminarios y clases especiales'),
        ('Calendario', '/calendario/', 'Cierres, cambios, exámenes y seminarios'),
        ('Fuera del dojo', '/fuera-del-dojo/', 'Lo que hacemos lejos del tatami'),
    ]),
    ('Media', '#A5C8D1', [
        ('Galería', '/galeria/', 'Álbumes, publicaciones y vídeos'),
        ('Prensa y TV', '/prensa-y-tv/', 'Dónde nos han sacado'),
    ]),
    ('Contacto y acceso', '#064F6E', [
        ('Contacto', '/contacto/', 'Escríbenos'),
        ('Acceso', '/acceso/', 'Los tres espacios y cómo llegar'),
    ]),
    ('Legal', '#5c6a70', [
        ('Aviso legal', '/aviso-legal/', 'Titularidad y condiciones'),
        ('Privacidad', '/politica-privacidad/', 'Qué datos tratamos'),
        ('Cookies', '/politica-cookies/', 'Qué se guarda y por qué'),
        ('Accesibilidad', '/accesibilidad/', 'Conformidad y limitaciones'),
    ]),
]

MAP_TOP = """
<header class="top w"><h1>Mapa del sitio</h1>
<p class="lede">Todas las páginas, en los cuatro idiomas. Si has llegado aquí es porque
   buscabas algo concreto y no lo encontrabas: dilo y lo arreglamos.</p></header>"""

MAP_A_CSS = """
.m-plan{padding:1rem 0 5rem}
.m-row{display:grid;grid-template-columns:13rem 1fr;gap:2.6rem;padding:2rem 0;
  border-top:1px solid var(--line);align-items:start}
.m-row:last-child{border-bottom:1px solid var(--line)}
.m-lab{position:sticky;top:1.5rem}
.m-lab h2{font-size:.86rem;letter-spacing:.14em;text-transform:uppercase;
  border-left:3px solid var(--c);padding-left:.8rem;line-height:1.4}
.m-lab .n{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.6rem;
  letter-spacing:.16em;color:var(--mute);margin-top:.5rem;padding-left:1.05rem}
.m-cells{display:grid;grid-template-columns:repeat(3,1fr);border-top:1px solid var(--line);
  border-left:1px solid var(--line)}
.m-cell{background:#fff;padding:1rem 1.05rem 1.1rem;display:block;text-decoration:none;
  color:inherit;position:relative;border-right:1px solid var(--line);
  border-bottom:1px solid var(--line)}
.m-cell:hover{background:#fffdf0}
.m-cell b{display:block;font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-weight:400;
  font-size:1rem;letter-spacing:.02em;color:var(--ink)}
.m-cell .u{display:block;font-family:ui-monospace,'SF Mono',Menlo,monospace;font-size:.68rem;
  color:var(--mute);margin-top:.25rem}
.m-cell .d{display:block;font-size:.8rem;line-height:1.6;color:var(--mute);margin-top:.5rem}
.m-cell .lg{display:flex;gap:.35rem;margin-top:.7rem}
.m-cell .lg span{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.54rem;
  letter-spacing:.1em;text-transform:uppercase;color:var(--mute);border:1px solid var(--line);
  padding:.12rem .3rem}
.m-cell:hover .lg span{border-color:var(--ink);color:var(--ink)}
@media(max-width:991.98px){.m-row{grid-template-columns:1fr;gap:1rem}.m-lab{position:static}
  .m-cells{grid-template-columns:1fr 1fr}}
@media(max-width:575.98px){.m-cells{grid-template-columns:1fr}}
"""


def map_a():
    o = [MAP_TOP, '<div class="m-plan w">']
    for name, color, items in TREE:
        o.append('<div class="m-row"><div class="m-lab"><h2 style="--c:%s">%s</h2>'
                 '<p class="n">%d páginas</p></div><div class="m-cells">' % (color, name, len(items)))
        for t, u, d in items:
            o.append('<a class="m-cell" href="%s"><b>%s</b><span class="u">%s</span>'
                     '<span class="d">%s</span><span class="lg"><span>ES</span><span>CA</span>'
                     '<span>EN</span><span>JA</span></span></a>' % (u, t, u, d))
        o.append('</div></div>')
    o.append('</div>')
    return ''.join(o)


MAP_B_CSS = """
.m-idx{padding:1rem 0 5rem;columns:2;column-gap:4rem}
.m-e{break-inside:avoid;padding:.7rem 0;border-bottom:1px solid var(--line);
  display:grid;grid-template-columns:1fr auto;gap:1rem;align-items:baseline}
.m-e a{color:var(--ink);text-decoration:none;font-size:1rem;
  font-family:Futura,'Trebuchet MS',Arial,sans-serif;letter-spacing:.02em}
.m-e a:hover{border-bottom:2px solid var(--acc)}
.m-e .sec{display:block;font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.56rem;
  letter-spacing:.16em;text-transform:uppercase;color:var(--c);margin-bottom:.25rem}
.m-e .lg{display:flex;gap:.45rem}
.m-e .lg a{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.58rem;
  letter-spacing:.1em;text-transform:uppercase;color:var(--mute)}
.m-e .lg a:hover{color:var(--ink);border-bottom:1px solid var(--ink)}
.m-letter{break-inside:avoid;break-after:avoid;font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:1.5rem;
  color:var(--ink);border-bottom:2px solid var(--ink);padding-bottom:.3rem;
  margin:1.8rem 0 .4rem}
.m-letter:first-child{margin-top:0}
@media(max-width:767.98px){.m-idx{columns:1}}
"""


def map_b():
    rows = []
    for name, color, items in TREE:
        for t, u, d in items:
            rows.append((t, u, name, color))
    rows.sort(key=lambda r: r[0].lower())
    o = [MAP_TOP.replace('Todas las páginas, en los cuatro idiomas.',
                         'Todas las páginas por orden alfabético, como el índice del final '
                         'de un libro.'), '<div class="m-idx w">']
    letter = None
    for t, u, sec, color in rows:
        ini = t[0].upper()
        if ini != letter:
            letter = ini
            o.append('<p class="m-letter">%s</p>' % ini)
        o.append('<div class="m-e"><div><span class="sec" style="--c:%s">%s</span>'
                 '<a href="%s">%s</a></div><span class="lg">'
                 '<a href="%s">es</a><a href="/ca%s">ca</a><a href="/en%s">en</a>'
                 '<a href="/ja%s">ja</a></span></div>' % (color, sec, u, t, u, u, u, u))
    o.append('</div>')
    return ''.join(o)


for f, title, css, body in (
        ('accesibilidad.html', 'Declaración de accesibilidad', A11Y_CSS, A11Y),
        ('mapa-a.html', 'Mapa del sitio', MAP_A_CSS, map_a()),
        ('mapa-b.html', 'Mapa del sitio', MAP_B_CSS, map_b())):
    io.open(os.path.join(OUT, f), 'w', encoding='utf-8').write(SHELL % (title, css, body))
    print('  ' + f)
