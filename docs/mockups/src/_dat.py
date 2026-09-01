# -*- coding: utf-8 -*-
"""Real data. Nothing invented, nothing rounded up."""
import re, io, os, collections

ROOT = '/Applications/MAMP/htdocs/aikidomusubi.com'
TODAY = '2026-08-23'                       # Sunday
MONTH = {'01': 'enero', '02': 'febrero', '03': 'marzo', '04': 'abril', '05': 'mayo',
         '06': 'junio', '07': 'julio', '08': 'agosto', '09': 'septiembre',
         '10': 'octubre', '11': 'noviembre', '12': 'diciembre'}
MON3 = {k: (v[:3] if k != '09' else 'sep') for k, v in MONTH.items()}


# ── gallery ────────────────────────────────────────────────────────────────
def gallery():
    s = io.open(os.path.join(ROOT, '_data/gallery.yml'), encoding='utf-8').read()
    blocks = re.findall(r'\n  - type:\s*(\w+)(.*?)(?=\n  - type:|\Z)', s, re.S)
    per_year, types, rows = collections.Counter(), collections.Counter(), []
    for t, b in blocks:
        if re.search(r'show:\s*false', b):
            continue
        d = re.search(r'date_iso:\s*"?([\d-]+)', b)
        th = re.search(r'thumb:\s*"?([^"\n]+)', b)
        if not d:
            continue
        per_year[d.group(1)[:4]] += 1
        types[t] += 1
        if th and os.path.isfile(os.path.join(ROOT, 'images/%s.webp' % th.group(1).strip())):
            rows.append((d.group(1), th.group(1).strip(), t))
    rows.sort(reverse=True)
    return per_year, types, rows


# ── events ─────────────────────────────────────────────────────────────────
# The stored titles are "Emilio Cardia Shihan 6.º Dan Aikikai" — a name and a
# grade, which is right on the event's own card and wrong in a list of things
# that happened. `category` already distinguishes seminar / masterclass /
# collaboration, so a descriptive line can be composed rather than rewritten.
RANK = re.compile(r'\s+(\d)\.º Dan (Aikikai|Birankai)\s*$')


def events():
    out = []
    for f in sorted(os.listdir(os.path.join(ROOT, '_events'))):
        if not f.endswith('.md'):
            continue
        s = io.open(os.path.join(ROOT, '_events', f), encoding='utf-8').read()
        g = lambda k: (re.search(r'^%s:\s*"?([^"\n]*)"?\s*$' % k, s, re.M) or [None, ''])[1]
        title = g('title_es')
        cat = g('category')
        d0, d1 = f[:10], g('date_to').strip()
        m = RANK.search(title)
        name, grade = (title[:m.start()], '%s.º dan %s' % (m.group(1), m.group(2))) if m else (title, '')
        multi = bool(d1 and d1 != 'blank' and d1 != d0)
        if cat == 'collaboration':
            label = name                                  # already descriptive
        elif cat == 'seminar':
            label = ('Seminario internacional de %s en Barcelona' if multi
                     else 'Seminario de %s en Barcelona') % name
        else:
            label = 'Masterclass de %s en el dojo' % name
        out.append(dict(date=d0, to=d1, cat=cat, name=name, grade=grade, label=label))
    return out


# ── the week, as it actually is right now ──────────────────────────────────
# August is an exception written into _data/calendar.yml: Tue and Thu only,
# 18:30-20:30, "el resto de la semana habitual no se imparte". Plus a Saturday
# grading-preparation class that runs until 5 December. A panel that showed the
# ordinary timetable this week would be showing a week that is not happening.
NEXT_SEVEN = [
    ('Dom', '23', True, []),
    ('Lun', '24', False, []),
    ('Mar', '25', False, [('#E2625E', 'Aikido', '18:30 · J. M. Molina'),
                          ('#E2625E', 'Aikido', '19:30 · J. M. Pérez')]),
    ('Mié', '26', False, []),
    ('Jue', '27', False, [('#E2625E', 'Aikido', '18:30 · J. M. Molina'),
                          ('#E2625E', 'Aikido', '19:30 · J. M. Pérez')]),
    ('Vie', '28', False, []),
    ('Sáb', '29', False, [('#FFF200', 'Preparación de exámenes', '10:00 · J. M. Pérez')]),
]

REGULAR_WEEK = [
    ('Lun', [('#B7C2A9', 'Iaijutsu', '20:00'), ('#A5C8D1', 'Judo', '18:30'),
             ('#E2625E', 'Aikido', '19:00 · UB'), ('#E2625E', 'Aikido', '20:00 · Sant Adrià')]),
    ('Mar', [('#E2625E', 'Aikido', '18:30'), ('#E2625E', 'Aikido', '19:30 · principiantes'),
             ('#E2625E', 'Aikido', '20:30'), ('#FBE6A0', 'Karate', '21:30')]),
    ('Mié', [('#A5C8D1', 'Judo', '18:30'), ('#E2625E', 'Aikido', '19:00 · UB'),
             ('#E2625E', 'Aikido', '20:00'), ('#E2625E', 'Aikido', '20:15 · Sant Adrià')]),
    ('Jue', [('#E2625E', 'Aikido', '18:30'), ('#E2625E', 'Aikido', '19:30 · armas'),
             ('#E2625E', 'Aikido', '20:30')]),
    ('Vie', [('#E2625E', 'Aikido', '19:00'), ('#FBE6A0', 'Karate', '20:00')]),
    ('Sáb', [('#E2625E', 'Aikido', '07:30'), ('#B7C2A9', 'Iaijutsu', '08:00 · mensual'),
             ('#FBE6A0', 'Karate', '11:00')]),
    ('Dom', []),
]

# from _data/calendar.yml, everything ahead of TODAY that a reader would act on
AHEAD = [
    ('2026-08-29', 'extra', 'Preparación de exámenes', 'Cada sábado, 10:00, hasta el 5 de diciembre'),
    ('2026-09-01', 'change', 'Vuelta al horario habitual', 'Termina el horario reducido de agosto'),
    ('2026-09-11', 'closure', 'Diada de Catalunya', 'El dojo cierra'),
    ('2026-10-12', 'closure', 'Fiesta Nacional', 'El dojo cierra'),
    ('2026-12-08', 'closure', 'La Inmaculada', 'El dojo cierra'),
]

LINE = [
    ('1883–1969', 'Morihei Ueshiba', 'Ō-Sensei, fundador del aikido', ''),
    ('desde 1931', 'Aikido Hombu Dojo', 'Tokio, la sede mundial del Aikido',
     'Aikido Doshu Ueshiba Moriteru · Aikido Hombu Dojo-cho Ueshiba Mitsuteru'),
    ('desde 2020', 'Arashi Group',
     'Organización reconocida por el Aikido Hombu Dojo a la que pertenecemos',
     'Vínculo a través de Tsuruzo Miyamoto Sensei, 8.º dan'),
    ('desde 2008', 'Aikido Musubi', 'Badalona, Barcelona', ''),
]

# Six you meet on the first day, then six you pick up later. The second set is
# revealed by a button, and it ends pointing at the glossary page to come.
WORDS = [
    ('道場', 'dōjō', 'El lugar donde se estudia el camino. No es un gimnasio: se entra y se sale saludando.'),
    ('稽古', 'keiko', 'La práctica. Literalmente «pensar en lo antiguo»: se repite algo que otros repitieron antes.'),
    ('礼', 'rei', 'El saludo. Abre y cierra la clase, y también cada práctica con cada compañero.'),
    ('受身', 'ukemi', 'La caída. La mitad del aikido consiste en aprender a recibir sin romperse.'),
    ('稽古着', 'keikogi', 'La ropa de práctica. Para las primeras clases basta con manga larga.'),
    ('産靈', 'musubi', 'El nudo: lo que une dos cosas y las deja unidas. De ahí el nombre del dojo.'),
]

WORDS_MORE = [
    ('取り・受け', 'tori · uke', 'Quien hace la técnica y quien la recibe. Se alternan sin parar: nadie es siempre uno de los dos.'),
    ('正座', 'seiza', 'Sentarse sobre los talones. Es como empieza y termina cada clase.'),
    ('お願いします', 'onegaishimasu', '«Te lo pido, por favor.» Lo que se dice al compañero antes de practicar con él.'),
    ('ありがとうございました', 'arigatō gozaimashita', '«Muchas gracias.» Lo que se le dice al terminar.'),
    ('段・級', 'dan · kyū', 'Los grados. Los kyu los examina el dojo; los dan quedan registrados en Tokio.'),
    ('師範', 'shihan', '«Modelo a seguir.» El título de los maestros de grado alto que vienen a dar seminarios.'),
]

LINKS_MAIN = [
    ('Aikikai Foundation', 'aikikai.or.jp', 'http://www.aikikai.or.jp/'),
    ('International Aikido Federation', 'aikido-international.org',
     'http://www.aikido-international.org/'),
    ('Arashi Group', 'aikidoarashigroup.com', 'http://aikidoarashigroup.com/'),
]

LINKS_DOJOS = [
    ('Sandokai Aikido Kyoto', 'Japón', 'aikidokyoto.com', 'https://www.aikidokyoto.com/'),
    ('Aikido Sanshinkai', 'Japón', 'aikidosanshin.wixsite.com',
     'https://aikidosanshin.wixsite.com/sanshinkai'),
    ('Aioikai · Aikido Kobe Sanda Dojo', 'Japón', 'lares.dti.ne.jp',
     'http://www.lares.dti.ne.jp/~horii'),
    ('Aikido Harukaze', 'Japón', 'aikido-harukaze.com', 'https://aikido-harukaze.com/'),
    ('Aikikai Corsico', 'Italia', 'aikikaicorsico.it', 'https://aikikaicorsico.it/'),
    ('Aikikai Milano', 'Italia', 'aikikaimilano.it', 'http://www.aikikaimilano.it/'),
    ('Aikido Verona', 'Italia', 'veronaikido.it', 'https://www.veronaikido.it/'),
    ('Aikido Watanabe Dojo', 'Italia', 'aikidowatanabedojo.it',
     'https://aikidowatanabedojo.it/'),
    ('Aikido Palestra Fujiyama Pietrasanta', 'Italia', 'aikido.palestrafujiyama.com',
     'https://aikido.palestrafujiyama.com/'),
    ('Venice Aikikai Birankai', 'Italia', 'facebook.com',
     'https://www.facebook.com/veniceaikikai.birankai/'),
    ('Wabi Aikido House', 'Italia', 'taplink.cc', 'https://taplink.cc/wabiaikidohouse'),
    ('Scottish and Borders Birankai', 'Escocia', 'scottishandbordersbirankai.com',
     'http://www.scottishandbordersbirankai.com/'),
    ('Thistle Aikikai', 'Escocia', 'thistleaikikai.com', 'http://thistleaikikai.com/'),
    ('Aikido of London', 'Inglaterra', 'aikidooflondon.com', 'https://aikidooflondon.com/'),
    ('Kokoro Aikido', 'Alemania', 'kokoro-aikido.de', 'https://www.kokoro-aikido.de/'),
    ('Hakken Dojo', 'Rumanía', 'aikido-aikikai.ro', 'https://www.aikido-aikikai.ro/'),
    ('Montérégie Aikikai', 'Canadá', 'monteregieaikikai.com',
     'https://www.monteregieaikikai.com/'),
    ('Dojo Feilen Meishūkan', 'Barcelona', 'aikifeilen.org', 'https://www.aikifeilen.org/'),
]

LINKS_TAIL = [
    ('Dónde entrenamos', [
        ('Poliesportiu Municipal Marina-Besòs', 'marinabesos.net', 'https://marinabesos.net/'),
        ('Facultat de Dret, Universitat de Barcelona', 'web.ub.edu',
         'https://web.ub.edu/es/web/facultat-dret/')]),
    ('Material', [
        ('Iwata Co.', 'iwataco.com', 'https://iwataco.com/', 'Tienda de material de artes marciales')]),
    ('Divulgación', [
        ('Budo Cool', 'budocool.com', 'https://www.budocool.com/', 'Creador de contenido')]),
]


VENUES = [('access-information-NdxqmVbV-00', 'Badalona',
           "Av. d'Alfons XIII, 351", 'Instalaciones Deportivas Badalona Sur'),
          ('access-information-NdxqmVbV-01', 'Sant Adrià de Besòs',
           'Poliesportiu Marina-Besòs', 'Carrer Dolores Ibarruri, s/n'),
          ('access-information-NdxqmVbV-02', 'Universitat de Barcelona',
           'Facultat de Dret', 'Av. Diagonal, 684')]
