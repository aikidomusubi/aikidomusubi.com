# -*- coding: utf-8 -*-
"""Content for the three Resources proposals.

Real material, not lorem: the documents the dojo actually hands out, the five
grading programmes, the weapons sheets, and a short reading list. The three
mockups render THE SAME content so what is being compared is the structure and
the reading experience, not the copy.
"""

# ---------------------------------------------------------------------------
# kind:  pdf | html | book | link
# A `kind` is not a file format, it is what the reader does with the thing:
# download it, read it here, borrow or buy it, or go somewhere else.
# ---------------------------------------------------------------------------

TRAMITES = [
    ('Hoja de inscripción', 'Datos, actividad y cuota. Se entrega firmada en el dojo o por correo.',
     'pdf', '210 KB', 'ES CA EN JA'),
    ('Autorización de uso de imagen', 'Para aparecer en fotos y vídeos del dojo. Revocable en cualquier momento.',
     'pdf', '180 KB', 'ES CA EN JA'),
    ('Autorización para menores', 'La firman padres, madres o tutores. Obligatoria por debajo de 14 años.',
     'pdf', '195 KB', 'ES CA'),
    ('Orden de domiciliación SEPA', 'Para la cuota mensual. Sólo si eliges pago por banco.',
     'pdf', '120 KB', 'ES CA'),
]

EXAMEN = [
    ('5.º kyū', 'El primero. Ocho técnicas, tres ataques y el ukemi que las acompaña.',
     '20 días de práctica', 8),
    ('4.º kyū', 'Entran suwariwaza y el primer trabajo contra dos ataques distintos.',
     '40 días desde 5.º', 14),
    ('3.er kyū', 'Aparecen hanmi handachi y las primeras proyecciones de cadera.',
     '60 días desde 4.º', 21),
    ('2.º kyū', 'Ushirowaza completo y el programa de jō empieza a contar.',
     '80 días desde 3.º', 27),
    ('1.er kyū', 'Todo lo anterior, más jiyū waza y el trabajo con armas.',
     '100 días desde 2.º', 34),
]

ARMAS = [
    ('36 técnicas básicas de jō', 'El programa de Birankai, numerado. Base del trabajo de jō en el dojo.',
     'html', '—', 'ES CA EN JA'),
    ('31 no jō kata', 'La forma de treinta y una cuentas, con el desglose por tiempos.',
     'pdf', '340 KB', 'ES EN'),
    ('Ken suburi · 7 cortes', 'Los siete cortes de suburi con bokken, y para qué sirve cada uno.',
     'html', '—', 'ES CA EN JA'),
    ('Kumijō · 10 formas', 'Las diez formas por parejas. Requiere el programa de 31 no jō.',
     'pdf', '410 KB', 'ES EN'),
]

ETIQUETA = [
    ('Etiqueta del dojo · reihō', 'Cómo se entra, cómo se saluda, cómo se trata al compañero.',
     'html', '—', 'ES CA EN JA'),
    ('Normas de la sala', 'Uso del tatami, vestuarios, material y horarios de acceso.',
     'pdf', '160 KB', 'ES CA'),
    ('Guía de la primera clase', 'Qué llevar, a qué hora llegar y qué va a pasar durante esa hora.',
     'html', '—', 'ES CA EN JA'),
]

LECTURAS = [
    ('Budo. Enseñanzas del fundador del Aikido', 'Morihei Ueshiba',
     'El manual de 1938, con fotografías del propio Ō-Sensei.', 'book',
     'Biblioteques de Barcelona · Amazon'),
    ('El espíritu del Aikido', 'Kisshomaru Ueshiba',
     'El hijo del fundador explicando qué se hereda y qué se cambia.', 'book',
     'Biblioteques de Barcelona · Amazon'),
    ('Aikido and the Dynamic Sphere', 'Westbrook &amp; Ratti',
     'El clásico ilustrado de 1970. Sigue siendo el mejor dibujo de un ukemi.', 'book',
     'Amazon'),
    ('Total Aikido. The Master Course', 'Gozo Shioda',
     'Shioda es Yoshinkan, no Aikikai, y por eso mismo enseña mucho.', 'book',
     'Amazon'),
    ('Aikido Journal', 'Stanley Pranin (ed.)',
     'Archivo histórico y entrevistas. Décadas de material, en abierto.', 'link',
     'aikidojournal.com'),
    ('Aikikai Hombu Dojo · vídeos', 'Aikikai Foundation',
     'Demostraciones anuales y material del honbu, en su canal oficial.', 'link',
     'youtube.com/@aikikai'),
]

GROUPS = [
    ('tramites', 'Trámites', 'Los papeles que hay que firmar una vez',
     'Cuatro documentos. Se rellenan, se firman y se entregan; después no vuelves a mirarlos.',
     TRAMITES),
    ('examen', 'Programa de examen', 'De 5.º a 1.er kyū',
     'El contenido de cada examen de kyū, con los días mínimos de práctica y las técnicas que entran.',
     None),
    ('armas', 'Armas', 'Jō, bokken y tantō',
     'Los programas de armas que se siguen en el dojo, con la numeración que se usa en clase.',
     ARMAS),
    ('etiqueta', 'Etiqueta y normas', 'Cómo funciona el tatami',
     'Lo que conviene saber antes de la primera clase y lo que se espera después.',
     ETIQUETA),
    ('lecturas', 'Lecturas', 'Libros y material de estudio',
     'Nada de esto lo publicamos nosotros. Está en la biblioteca pública o se compra.',
     None),
]

TOTAL = len(TRAMITES) + len(EXAMEN) + len(ARMAS) + len(ETIQUETA) + len(LECTURAS)
