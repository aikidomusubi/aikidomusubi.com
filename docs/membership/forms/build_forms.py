#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The paper forms the dojo prints and keeps signed: image use, and the
consent of a parent or guardian for a member under 18.

Separate from the enrolment form on purpose. Consent to publish somebody's
picture must be free and specific (RGPD art. 7, LO 1/1982), so it cannot be a
condition of membership or buried in it, and it can be withdrawn on its own.

    python3 docs/membership/forms/build_forms.py

Writes autorizacion-imagen-es.html and autoritzacio-imatge-ca.html beside this
file, A4 and print-ready; open one and print, or "Save as PDF". The
association's details are copied from _data/footer.yml, so a change of name or
address is made there and the forms are rebuilt.
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..', '..')


def footer_ui(key):
    s = open(os.path.join(ROOT, '_data', 'footer.yml'), encoding='utf-8').read()
    m = re.search(rf'^\s+{key}:\s+"([^"]*)"', s, re.M)
    return m.group(1).replace('<br>', ', ') if m else ''


ORG, CIF, ADDRESS, REG = footer_ui('org'), footer_ui('cif'), footer_ui('address'), footer_ui('registry')

CSS = """
@page{size:A4;margin:11mm 15mm}
*{box-sizing:border-box}
body{margin:0;font:9.5pt/1.4 "Noto Sans",Arial,sans-serif;color:#111314}
.sheet{max-width:178mm;margin:0 auto}
header{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:2.5pt solid #111314;padding-bottom:3mm;margin-bottom:5mm}
header b{font:700 14pt/1.1 Futura,"Trebuchet MS",Arial,sans-serif;letter-spacing:.04em;text-transform:uppercase}
header span{font-size:8pt;text-align:right;color:#3D4A50}
h1{font:700 15pt/1.2 Futura,"Trebuchet MS",Arial,sans-serif;margin:0 0 1mm}
.lede{margin:0 0 4mm;color:#3D4A50}
h2{font:700 10pt/1.2 Futura,"Trebuchet MS",Arial,sans-serif;text-transform:uppercase;letter-spacing:.06em;margin:3.5mm 0 1.8mm;padding-top:1.8mm;border-top:.6pt solid #bbb}
.line{display:flex;gap:4mm;margin:0 0 3mm}
.line label{flex:1;display:flex;gap:2mm;align-items:flex-end;white-space:nowrap}
.line label i{flex:1;border-bottom:.6pt solid #111314;height:5mm}
.box{display:flex;gap:2.5mm;align-items:flex-start;margin:0 0 2mm}
.box::before{content:"";flex:none;width:4mm;height:4mm;border:.8pt solid #111314;margin-top:.6mm}
p{margin:0 0 2mm}
.small{font-size:8pt;color:#3D4A50}
.sign{display:grid;grid-template-columns:1fr 1fr;gap:8mm;margin-top:9mm}
.sign div{border-top:.6pt solid #111314;padding-top:1.5mm;font-size:8.5pt}
.legal{margin-top:6mm;border:.6pt solid #bbb;padding:2.5mm 3mm}
.legal p{font-size:7.6pt;line-height:1.4;margin:0 0 1mm}
@media screen{body{background:#E9E8E3;padding:10mm 0}.sheet{background:#fff;padding:14mm 16mm;max-width:210mm;box-shadow:0 2px 12px rgba(0,0,0,.15)}}
"""

T = {
 'es': dict(
  file='autorizacion-imagen-es.html', lang='es',
  title='Autorización de uso de imagen',
  title2='y consentimiento de madre, padre o tutor',
  lede='Una por persona socia. Es voluntaria y no condiciona la pertenencia a la asociación.',
  h_person='1. La persona socia', name='Nombre y apellidos', born='Fecha de nacimiento (si es menor)',
  h_guardian='2. Solo si es menor de 18 años: madre, padre o tutor/a legal',
  g_name='Nombre y apellidos', g_id='DNI / NIE', g_contact='Teléfono o correo',
  g_consent=('Como madre, padre o tutor/a legal, doy mi consentimiento para que la persona menor indicada '
             'sea socia de la asociación y participe en sus actividades, como prevén los estatutos (art. 4), '
             'y, si es menor de 14 años, para el tratamiento de sus datos personales con ese fin.'),
  h_image='3. Fotos y vídeos',
  image_intro=('En clases, cursos, exámenes y eventos, la asociación hace fotografías y vídeos. '
               'Marque lo que autoriza; puede marcar varias opciones, o solo la última.'),
  opts=['Uso interno: el archivo de la asociación y los grupos de mensajería de socios, no públicos.',
        'La web de la asociación (aikidomusubi.com).',
        'Las redes sociales de la asociación (Instagram, Facebook, YouTube).',
        'Material impreso de difusión: carteles y folletos.',
        'No autorizo el uso de mi imagen, o de la de la persona menor.'],
  image_terms=('La autorización es gratuita y no tiene plazo. Se puede retirar o cambiar en cualquier momento '
               'escribiendo a info@aikidomusubi.com: retiraremos de la web y de las redes de la asociación lo que '
               'nos indique, aunque no podemos recuperar lo que otras personas hayan copiado antes. Junto a la '
               'imagen de una persona menor nunca publicamos su nombre completo ni otros datos que la identifiquen.'),
  sign1='Firma de la persona socia (si tiene 14 años o más)', sign2='Firma de madre, padre o tutor/a (si es menor de 18)',
  place='En ______________________, a ____ de ______________ de 20____',
  legal_h='Información básica sobre protección de datos',
  legal=[f'<b>Responsable:</b> {ORG}, CIF {CIF}, {ADDRESS}. info@aikidomusubi.com.',
         '<b>Finalidad:</b> gestionar la pertenencia a la asociación y, solo en los usos marcados, difundir sus actividades con imágenes.',
         '<b>Base jurídica:</b> el consentimiento (RGPD art. 6.1.a; Ley Orgánica 1/1982, de protección del derecho a la propia imagen; para menores de 14 años, LOPDGDD art. 7), y la relación asociativa.',
         '<b>Destinatarios:</b> las imágenes publicadas son visibles para el público; las redes sociales pertenecen a empresas que pueden tratar los datos fuera de la UE, con las garantías que describe nuestra política de privacidad.',
         '<b>Derechos:</b> acceso, rectificación, supresión, oposición, limitación y portabilidad, y retirar el consentimiento, en info@aikidomusubi.com. Puede reclamar ante la Agencia Española de Protección de Datos (aepd.es).',
         '<b>Más información:</b> aikidomusubi.com/politica-privacidad/']),
 'ca': dict(
  file='autoritzacio-imatge-ca.html', lang='ca',
  title="Autorització d'ús d'imatge",
  title2='i consentiment de la mare, el pare o el tutor',
  lede="Una per persona sòcia. És voluntària i no condiciona la pertinença a l'associació.",
  h_person='1. La persona sòcia', name='Nom i cognoms', born='Data de naixement (si és menor)',
  h_guardian="2. Només si és menor de 18 anys: mare, pare o tutor/a legal",
  g_name='Nom i cognoms', g_id='DNI / NIE', g_contact='Telèfon o correu',
  g_consent=("Com a mare, pare o tutor/a legal, dono el meu consentiment perquè la persona menor indicada "
             "sigui sòcia de l'associació i participi en les seves activitats, com preveuen els estatuts (art. 4), "
             "i, si és menor de 14 anys, per al tractament de les seves dades personals amb aquesta finalitat."),
  h_image='3. Fotos i vídeos',
  image_intro=("A les classes, els cursos, els exàmens i els esdeveniments, l'associació fa fotografies i vídeos. "
               "Marqueu el que autoritzeu; podeu marcar diverses opcions, o només l'última."),
  opts=["Ús intern: l'arxiu de l'associació i els grups de missatgeria de socis, no públics.",
        "El web de l'associació (aikidomusubi.com).",
        "Les xarxes socials de l'associació (Instagram, Facebook, YouTube).",
        'Material imprès de difusió: cartells i fullets.',
        "No autoritzo l'ús de la meva imatge, o de la de la persona menor."],
  image_terms=("L'autorització és gratuïta i no té termini. Es pot retirar o canviar en qualsevol moment "
               "escrivint a info@aikidomusubi.com: retirarem del web i de les xarxes de l'associació el que ens "
               "indiqueu, tot i que no podem recuperar el que altres persones hagin copiat abans. Al costat de la "
               "imatge d'una persona menor no publiquem mai el seu nom complet ni altres dades que la identifiquin."),
  sign1='Signatura de la persona sòcia (si té 14 anys o més)', sign2='Signatura de la mare, el pare o el tutor/a (si és menor de 18)',
  place='A ______________________, ____ de ______________ de 20____',
  legal_h='Informació bàsica sobre protecció de dades',
  legal=[f'<b>Responsable:</b> {ORG}, CIF {CIF}, {ADDRESS}. info@aikidomusubi.com.',
         "<b>Finalitat:</b> gestionar la pertinença a l'associació i, només en els usos marcats, difondre'n les activitats amb imatges.",
         '<b>Base jurídica:</b> el consentiment (RGPD art. 6.1.a; Llei orgànica 1/1982, de protecció del dret a la pròpia imatge; per als menors de 14 anys, LOPDGDD art. 7), i la relació associativa.',
         '<b>Destinataris:</b> les imatges publicades són visibles per al públic; les xarxes socials pertanyen a empreses que poden tractar les dades fora de la UE, amb les garanties que descriu la nostra política de privadesa.',
         "<b>Drets:</b> accés, rectificació, supressió, oposició, limitació i portabilitat, i retirar el consentiment, a info@aikidomusubi.com. Podeu reclamar davant l'Agència Espanyola de Protecció de Dades (aepd.es) o l'Autoritat Catalana de Protecció de Dades (apdcat.gencat.cat).",
         '<b>Més informació:</b> aikidomusubi.com/ca/politica-privadesa/']),
}


def line(*labels):
    return '<div class="line">' + ''.join(f'<label>{l}: <i></i></label>' for l in labels) + '</div>'


def build(t):
    body = f"""<div class="sheet">
<header><b>{ORG}</b><span>CIF {CIF} · {ADDRESS}<br>info@aikidomusubi.com · aikidomusubi.com</span></header>
<h1>{t['title']}</h1><p class="lede"><b>{t['title2']}.</b> {t['lede']}</p>
<h2>{t['h_person']}</h2>{line(t['name'])}{line(t['born'])}
<h2>{t['h_guardian']}</h2>{line(t['g_name'])}{line(t['g_id'], t['g_contact'])}
<div class="box"><span>{t['g_consent']}</span></div>
<h2>{t['h_image']}</h2><p>{t['image_intro']}</p>
{''.join(f'<div class="box"><span>{o}</span></div>' for o in t['opts'])}
<p class="small">{t['image_terms']}</p>
<p style="margin-top:4mm">{t['place']}</p>
<div class="sign"><div>{t['sign1']}</div><div>{t['sign2']}</div></div>
<div class="legal"><p><b>{t['legal_h']}</b></p>{''.join(f'<p>{p}</p>' for p in t['legal'])}</div>
</div>"""
    html = (f'<!doctype html><html lang="{t["lang"]}"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1"><title>{t["title"]}</title>'
            f'<style>{CSS}</style></head><body>{body}</body></html>\n')
    with open(os.path.join(HERE, t['file']), 'w', encoding='utf-8') as f:
        f.write(html)
    print('  docs/membership/forms/' + t['file'])


if __name__ == '__main__':
    for t in T.values():
        build(t)
