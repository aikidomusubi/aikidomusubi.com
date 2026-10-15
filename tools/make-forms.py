#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The dojo's paper forms, as PDFs with fields that can be filled in.

    python3 tools/make-forms.py

Writes nine files into /files/, where the Resources page finds them:

    resources-uStNjtHz-inscripcion-{es,ca,en}.pdf   enrolment, one per person
    resources-uStNjtHz-imagen-{es,ca,en}.pdf        photos and videos, voluntary
    resources-uStNjtHz-menores-{es,ca,en}.pdf       a parent's or guardian's consent

WHY FILLABLE. A member fills the form on their phone (Files on iOS, the PDF
viewer of Chrome or Drive on Android, Acrobat anywhere), saves it, and prints
it at the dojo or sends it: no handwriting to misread. It still prints blank
and is filled by hand just as well. Every field has a tooltip naming it,
which is what a screen reader announces.

WHY THREE FORMS AND NOT ONE. Consent to publish somebody's picture has to be
free and specific (RGPD art. 7, LO 1/1982), so it cannot be a condition of
joining or sit inside the enrolment form; and the parental consent is only for
minors. The statutes (art. 4) ask for it for everyone under 18.

THE FACTS come from the site's own data: the name, CIF, address and registry
number from _data/footer.yml, the rooms from _data/venues.yml. A change there
is a re-run here, never an edit of a PDF.

Needs reportlab and fonttools (for the faces), in a throwaway venv, as
tools/subset-ja-fonts.py explains for fontTools. Not project dependencies.
"""
import io
import os
import re
import sys

try:
    from fontTools.ttLib import TTFont
    from reportlab.lib.colors import HexColor, white
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont as RLTTFont
    from reportlab.pdfgen import canvas
except ImportError as e:
    sys.exit(f"needs reportlab and fonttools in a throwaway venv ({e})")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "files")
PFX = "resources-uStNjtHz-"

BLACK = HexColor("#111314")
INK = HexColor("#3D4A50")
MUTE = HexColor("#5A686E")
LINE = HexColor("#9AA3A7")
FIELD = HexColor("#F4F6F7")
YELLOW = HexColor("#FFF200")


def ui(key):
    s = open(os.path.join(ROOT, "_data", "footer.yml"), encoding="utf-8").read()
    m = re.search(rf'^\s+{key}:\s+"([^"]*)"', s, re.M)
    return m.group(1).replace("<br>", ", ") if m else ""


ORG, CIF, ADDRESS, REG = ui("org"), ui("cif"), ui("address"), ui("registry")


def rooms(lang):
    """The rooms we teach in, from _data/venues.yml: each venue's short name,
    except the dojo itself, whose name is the association's and would say
    nothing on this form, so it is called by its town."""
    s = open(os.path.join(ROOT, "_data", "venues.yml"), encoding="utf-8").read()
    names = []
    for block in re.split(r"\n  - id: ", s)[1:]:
        vid = block.split("\n", 1)[0].strip()
        m = re.search(rf'^    name:\n(?:\s+\w\w: .*\n)*?\s+{lang}: "([^"]+)"', block, re.M)
        if not m:
            continue
        name = m.group(1)
        if vid == "aikido-musubi":
            name = {"es": "dojo de Badalona", "ca": "dojo de Badalona", "en": "Badalona dojo"}[lang]
        if name not in names:
            names.append(name)
    return names


def faces():
    """Noto Sans, the site's own face, from the self-hosted WOFF2 files. The
    latin and latin-ext subsets are merged into one face, because a PDF string
    is drawn in a single font and the forms need both: "kyū" is in latin-ext."""
    from fontTools.merge import Merger
    for weight, name in ((400, "Noto"), (700, "NotoBold")):
        parts = []
        for sub in ("latin", "latin-ext"):
            f = TTFont(os.path.join(ROOT, "fonts", f"noto-sans-{weight}-{sub}.woff2"))
            f.flavor = None
            b = io.BytesIO()
            f.save(b)
            b.seek(0)
            parts.append(b)
        merged = Merger().merge(parts)
        buf = io.BytesIO()
        merged.save(buf)
        buf.seek(0)
        pdfmetrics.registerFont(RLTTFont(name, buf))


# ---------------------------------------------------------------------------
class Form:
    """A4, a cursor that moves down the page, and helpers for each kind of row."""

    L, R, TOP, BOTTOM = 15 * mm, A4[0] - 15 * mm, A4[1] - 12 * mm, 11 * mm

    def __init__(self, path, title, lang, subject):
        self.path = path
        self.c = canvas.Canvas(path, pagesize=A4)
        self.c.setTitle(title)
        self.c.setAuthor(ORG)
        self.c.setSubject(subject)
        self.c.setCreator("aikidomusubi.com, tools/make-forms.py")
        self.lang = lang
        self.y = self.TOP
        self.n = 0
        self.W = self.R - self.L

    def header(self, title, sub):
        c = self.c
        c.setFillColor(BLACK)
        c.setFont("NotoBold", 13)
        c.drawString(self.L, self.y - 4 * mm, ORG.upper())
        c.setFont("Noto", 7.2)
        c.setFillColor(INK)
        c.drawRightString(self.R, self.y - 1.5 * mm, f"CIF {CIF} · {ADDRESS}")
        c.drawRightString(self.R, self.y - 4.8 * mm, "info@aikidomusubi.com · aikidomusubi.com")
        self.y -= 7 * mm
        c.setStrokeColor(BLACK)
        c.setLineWidth(2)
        c.line(self.L, self.y, self.R, self.y)
        c.setFillColor(YELLOW)
        c.rect(self.L, self.y - 1.6 * mm, 22 * mm, 1.6 * mm, stroke=0, fill=1)
        self.y -= 9 * mm
        c.setFillColor(BLACK)
        c.setFont("NotoBold", 15)
        c.drawString(self.L, self.y, title)
        self.y -= 5.5 * mm
        self.para(sub, size=8.6, color=INK)
        self.y -= 1 * mm

    def h(self, text):
        c = self.c
        self.y -= 2.4 * mm
        c.setStrokeColor(LINE)
        c.setLineWidth(0.5)
        c.line(self.L, self.y, self.R, self.y)
        self.y -= 4.2 * mm
        c.setFillColor(BLACK)
        c.setFont("NotoBold", 9)
        c.drawString(self.L, self.y, text.upper())
        self.y -= 3 * mm

    def para(self, text, size=8.6, color=INK, font="Noto", indent=0, width=None, lead=1.38):
        """Wrapped text; **bold** runs are not supported, keep it plain."""
        c = self.c
        width = width or (self.W - indent)
        c.setFont(font, size)
        c.setFillColor(color)
        words = text.split(" ")
        line = ""
        for w in words:
            test = (line + " " + w).strip()
            if pdfmetrics.stringWidth(test, font, size) > width and line:
                c.drawString(self.L + indent, self.y, line)
                self.y -= size * lead
                line = w
            else:
                line = test
        if line:
            c.drawString(self.L + indent, self.y, line)
            self.y -= size * lead

    def fields(self, *specs, height=5.8 * mm):
        """One row of labelled text fields. spec = (label, share, name[, multiline])."""
        c = self.c
        gap = 4 * mm
        total = sum(s[1] for s in specs)
        avail = self.W - gap * (len(specs) - 1)
        x = self.L
        self.y -= 3.4 * mm
        label_y = self.y
        for spec in specs:
            label, share, name = spec[0], spec[1], spec[2]
            w = avail * share / total
            c.setFont("Noto", 7.4)
            c.setFillColor(MUTE)
            c.drawString(x, label_y, label)
            c.acroForm.textfield(
                name=name, tooltip=label, x=x, y=label_y - 1.2 * mm - height, width=w, height=height,
                fontName="Helvetica", fontSize=10, borderStyle="underlined", borderColor=BLACK,
                fillColor=FIELD, textColor=BLACK, borderWidth=0.6, forceBorder=True,
                fieldFlags="multiline" if len(spec) > 3 and spec[3] else "")
            x += w + gap
        self.y = label_y - 1.2 * mm - height - 1.2 * mm

    def check(self, name, text, size=8.6, bold=False):
        c = self.c
        box = 3.6 * mm
        self.y -= 2.2 * mm
        top = self.y
        c.acroForm.checkbox(name=name, tooltip=text[:120], x=self.L, y=top - box + 1.3 * mm, size=box,
                            buttonStyle="check", borderColor=BLACK, fillColor=white, textColor=BLACK,
                            borderWidth=0.7, forceBorder=True)
        self.para(text, size=size, color=BLACK, font="NotoBold" if bold else "Noto", indent=6 * mm)

    def radios(self, group, label, options):
        """A label, then options side by side: one may be chosen."""
        c = self.c
        self.y -= 3.4 * mm
        c.setFont("Noto", 7.4)
        c.setFillColor(MUTE)
        c.drawString(self.L, self.y, label)
        self.y -= 5 * mm
        x = self.L
        box = 3.4 * mm
        for value, text in options:
            c.acroForm.radio(name=group, tooltip=f"{label}: {text}", value=value, selected=False,
                             x=x, y=self.y - 0.6 * mm, size=box, buttonStyle="check", shape="square",
                             borderColor=BLACK, fillColor=white, textColor=BLACK, borderWidth=0.7, forceBorder=True)
            c.setFont("Noto", 8.6)
            c.setFillColor(BLACK)
            c.drawString(x + box + 1.6 * mm, self.y, text)
            x += box + 4 * mm + pdfmetrics.stringWidth(text, "Noto", 8.6) + 4 * mm
        self.y -= 2 * mm

    def signatures(self, *labels, place_label=None, date_label=None, prefix="sig"):
        c = self.c
        if place_label:
            self.fields((place_label, 2, f"{prefix}_place"), (date_label, 1, f"{prefix}_date"))
        self.y -= 13 * mm
        gap = 8 * mm
        w = (self.W - gap * (len(labels) - 1)) / len(labels)
        x = self.L
        for lab in labels:
            c.setStrokeColor(BLACK)
            c.setLineWidth(0.6)
            c.line(x, self.y, x + w, self.y)
            c.setFont("Noto", 7.4)
            c.setFillColor(MUTE)
            yy = self.y - 3.2 * mm
            # wrap the label under the line
            words, line = lab.split(" "), ""
            for wd in words:
                t = (line + " " + wd).strip()
                if pdfmetrics.stringWidth(t, "Noto", 7.4) > w and line:
                    c.drawString(x, yy, line)
                    yy -= 3 * mm
                    line = wd
                else:
                    line = t
            c.drawString(x, yy, line)
            x += w + gap
        self.y -= 9 * mm

    def legal(self, heading, lines):
        c = self.c
        size = 6.6
        self.y -= 2 * mm
        top = self.y
        # measure first: draw on a scratch height, then box it
        self.y -= 3.6 * mm
        c.setFont("NotoBold", size + 0.4)
        c.setFillColor(BLACK)
        c.drawString(self.L + 2.5 * mm, self.y, heading)
        self.y -= (size + 0.4) * 1.5
        for ln in lines:
            self.para(ln, size=size, color=INK, indent=2.5 * mm, width=self.W - 5 * mm, lead=1.32)
        self.y -= 1.2 * mm
        c.setStrokeColor(LINE)
        c.setLineWidth(0.5)
        c.rect(self.L, self.y, self.W, top - self.y, stroke=1, fill=0)

    def save(self):
        if self.y < self.BOTTOM:
            raise SystemExit(f"{os.path.basename(self.path)} overflows the page by {(self.BOTTOM - self.y) / mm:.1f} mm")
        print(f"  {os.path.basename(self.path):<44} {(self.y - self.BOTTOM) / mm:5.1f} mm to spare")
        self.c.showPage()
        self.c.save()


# ---------------------------------------------------------------------------
# The words. Three languages: Spanish, Catalan (Catalonia: the forms must be
# available in Catalan) and English (members from abroad). Japanese readers
# get the English one.

LEGAL_COMMON = {
    "es": ("Información básica sobre protección de datos", [
        f"Responsable: {ORG}, CIF {CIF}, {ADDRESS}. info@aikidomusubi.com.",
        "Derechos: acceso, rectificación, supresión, oposición, limitación y portabilidad, y retirar un consentimiento, en info@aikidomusubi.com. "
        "Puede reclamar ante la Agencia Española de Protección de Datos (aepd.es). Más información: aikidomusubi.com/politica-privacidad/"]),
    "ca": ("Informació bàsica sobre protecció de dades", [
        f"Responsable: {ORG}, CIF {CIF}, {ADDRESS}. info@aikidomusubi.com.",
        "Drets: accés, rectificació, supressió, oposició, limitació i portabilitat, i retirar un consentiment, a info@aikidomusubi.com. "
        "Podeu reclamar davant l'Agència Espanyola de Protecció de Dades (aepd.es). Més informació: aikidomusubi.com/ca/politica-privadesa/"]),
    "en": ("Data protection, in short", [
        f"Controller: {ORG}, CIF {CIF}, {ADDRESS}, Spain. info@aikidomusubi.com.",
        "Your rights: access, rectification, erasure, objection, restriction and portability, and withdrawing a consent, at info@aikidomusubi.com. "
        "You may complain to the Spanish Data Protection Agency (aepd.es). More: aikidomusubi.com/en/privacy-policy/"]),
}


def enrolment(lang):
    t = {
        "es": dict(
            title="Hoja de inscripción",
            sub="Solicitud para ser socio o socia, una por persona. Rellénala en el móvil o a mano. La cuota se paga aparte; "
                "si eres menor de 18 años, adjunta la autorización para menores.",
            h1="1. Datos personales", given="Nombre", family="Apellidos", born="Fecha de nacimiento (dd/mm/aaaa)",
            nat="Nacionalidad", doc="Documento de identidad", doc_opts=[("dni", "DNI"), ("nie", "NIE"), ("pas", "Pasaporte")],
            docno="Número del documento", addr="Dirección", cp="Código postal", town="Población",
            phone="Teléfono", email="Correo electrónico",
            h2="2. Tu práctica", where="Dónde entrenarás", grade="Grado actual, si tienes (kyū o dan)",
            since="Practicas desde (año)", before="Dojo o asociación anteriores",
            h3="3. En caso de urgencia, avisar a", ename="Nombre y apellidos", ephone="Teléfono", erel="Relación",
            h4="4. Declaración y solicitud",
            health="Declaro que no conozco ningún motivo de salud que me impida practicar aikido, y que avisaré a quien imparte la "
                   "clase de cualquier lesión o circunstancia que deba tener en cuenta.",
            apply=f"Solicito ser socio o socia de la {ORG}, y conozco y acepto sus estatutos (aikidomusubi.com/ca/estatuts) "
                  "y las condiciones de la cuota.",
            sign=("Firma de la persona socia", "Firma de madre, padre o tutor/a (si es menor de 18)"),
            place="Lugar", date="Fecha",
            purpose=["Finalidad: gestionar tu pertenencia a la asociación, las clases, tu licencia federativa y el seguro deportivo, "
                     "y registrar tus grados ante la Fundación Aikikai (Japón), que pide la nacionalidad. El documento de identidad lo piden "
                     "la federación y la aseguradora para la licencia.",
                     "Base jurídica: la relación asociativa que solicitas (RGPD art. 6.1.b) y las obligaciones legales de la asociación (art. 6.1.c). "
                     "El contacto de urgencia, tu interés vital y el de la persona indicada.",
                     "Destinatarios: la federación deportiva y su aseguradora; la Fundación Aikikai (Japón, país con decisión de adecuación de la "
                     "Comisión Europea). Conservación: mientras seas socio o socia y, después, los plazos legales (en general, 4 años)."]),
        "ca": dict(
            title="Full d'inscripció",
            sub="Sol·licitud per ser soci o sòcia, un per persona. Omple'l al mòbil o a mà. La quota es paga a part; "
                "si ets menor de 18 anys, adjunta l'autorització per a menors.",
            h1="1. Dades personals", given="Nom", family="Cognoms", born="Data de naixement (dd/mm/aaaa)",
            nat="Nacionalitat", doc="Document d'identitat", doc_opts=[("dni", "DNI"), ("nie", "NIE"), ("pas", "Passaport")],
            docno="Número del document", addr="Adreça", cp="Codi postal", town="Població",
            phone="Telèfon", email="Correu electrònic",
            h2="2. La teva pràctica", where="On entrenaràs", grade="Grau actual, si en tens (kyū o dan)",
            since="Practiques des de (any)", before="Dojo o associació anteriors",
            h3="3. En cas d'urgència, avisar", ename="Nom i cognoms", ephone="Telèfon", erel="Relació",
            h4="4. Declaració i sol·licitud",
            health="Declaro que no conec cap motiu de salut que m'impedeixi practicar aikido, i que avisaré qui fa la classe de "
                   "qualsevol lesió o circumstància que hagi de tenir en compte.",
            apply=f"Sol·licito ser soci o sòcia de l'{ORG}, i conec i accepto els seus estatuts (aikidomusubi.com/ca/estatuts) "
                  "i les condicions de la quota.",
            sign=("Signatura de la persona sòcia", "Signatura de la mare, el pare o el tutor/a (si és menor de 18)"),
            place="Lloc", date="Data",
            purpose=["Finalitat: gestionar la teva pertinença a l'associació, les classes, la llicència federativa i l'assegurança esportiva, "
                     "i registrar els teus graus davant la Fundació Aikikai (Japó), que demana la nacionalitat. El document d'identitat el "
                     "demanen la federació i l'asseguradora per a la llicència.",
                     "Base jurídica: la relació associativa que sol·licites (RGPD art. 6.1.b) i les obligacions legals de l'associació (art. 6.1.c). "
                     "El contacte d'urgència, el teu interès vital i el de la persona indicada.",
                     "Destinataris: la federació esportiva i la seva asseguradora; la Fundació Aikikai (Japó, país amb decisió d'adequació de la "
                     "Comissió Europea). Conservació: mentre siguis soci o sòcia i, després, els terminis legals (en general, 4 anys)."]),
        "en": dict(
            title="Enrolment form",
            sub="Application to become a member, one per person. Fill it in on your phone or by hand. The fee is paid separately; "
                "if you are under 18, add the consent for minors.",
            h1="1. Personal details", given="First name", family="Surnames", born="Date of birth (dd/mm/yyyy)",
            nat="Nationality", doc="Identity document", doc_opts=[("dni", "DNI"), ("nie", "NIE"), ("pas", "Passport")],
            docno="Document number", addr="Address", cp="Postcode", town="Town",
            phone="Phone", email="Email",
            h2="2. Your practice", where="Where you will train", grade="Current grade, if any (kyū or dan)",
            since="Practising since (year)", before="Previous dojo or association",
            h3="3. In an emergency, contact", ename="Full name", ephone="Phone", erel="Relationship",
            h4="4. Declaration and application",
            health="I declare that I know of no health reason that prevents me from practising aikido, and that I will tell the "
                   "instructor of any injury or circumstance they should take into account.",
            apply=f"I apply to become a member of the {ORG}, and I know and accept its statutes (aikidomusubi.com/ca/estatuts, in Catalan) "
                  "and the membership terms.",
            sign=("Signature of the member", "Signature of a parent or guardian (if under 18)"),
            place="Place", date="Date",
            purpose=["Purpose: to manage your membership of the association, the classes, your federation licence and sports insurance, "
                     "and to register your grades with the Aikikai Foundation (Japan), which asks for nationality. The identity document is "
                     "required by the federation and the insurer for the licence.",
                     "Legal basis: the membership you apply for (GDPR art. 6.1.b) and the association's legal obligations (art. 6.1.c). "
                     "The emergency contact: your vital interests and those of the person named.",
                     "Recipients: the sports federation and its insurer; the Aikikai Foundation (Japan, a country with a European Commission "
                     "adequacy decision). Kept while you are a member and then for the legal periods (generally 4 years)."]),
    }[lang]
    f = Form(os.path.join(OUT, f"{PFX}inscripcion-{lang}.pdf"), t["title"], lang, t["sub"])
    f.header(t["title"], t["sub"])
    f.h(t["h1"])
    f.fields((t["given"], 1, "given"), (t["family"], 2, "family"))
    f.fields((t["born"], 1, "born"), (t["nat"], 1, "nationality"))
    f.radios("doc_type", t["doc"], t["doc_opts"])
    f.fields((t["docno"], 1, "doc_number"), (t["phone"], 1, "phone"))
    f.fields((t["addr"], 1, "address"))
    f.fields((t["cp"], 1, "postcode"), (t["town"], 2, "town"), (t["email"], 3, "email"))
    f.h(t["h2"])
    f.fields((t["where"] + " (" + ", ".join(rooms(lang)) + ")", 1, "where"))
    f.fields((t["grade"], 2, "grade"), (t["since"], 1, "since"), (t["before"], 3, "before"))
    f.h(t["h3"])
    f.fields((t["ename"], 3, "emergency_name"), (t["ephone"], 2, "emergency_phone"), (t["erel"], 2, "emergency_relation"))
    f.h(t["h4"])
    f.check("health", t["health"])
    f.check("apply", t["apply"])
    f.signatures(*t["sign"], place_label=t["place"], date_label=t["date"])
    head, common = LEGAL_COMMON[lang]
    f.legal(head, [common[0]] + t["purpose"] + [common[1]])
    f.save()


def image(lang):
    t = {
        "es": dict(
            title="Autorización de uso de imagen",
            sub="Voluntaria, una por persona. No darla no cambia nada de tu cuota ni de tus clases, y puedes retirarla o cambiarla "
                "cuando quieras escribiendo a info@aikidomusubi.com.",
            h1="1. La persona socia", name="Nombre y apellidos",
            h2="2. Fotos y vídeos",
            intro="En clases, cursos, exámenes y eventos hacemos fotografías y vídeos. Marca lo que autorizas; puedes marcar varias "
                  "opciones, o solo la última.",
            opts=["Uso interno: el archivo de la asociación y los grupos de mensajería de socios, no públicos.",
                  "La web de la asociación (aikidomusubi.com).",
                  "Las redes sociales de la asociación (Instagram, Facebook, YouTube).",
                  "Material impreso de difusión: carteles y folletos."],
            no="No autorizo el uso de mi imagen, o de la de la persona menor.",
            terms="La autorización es gratuita y no tiene plazo. Si la retiras, quitamos de la web y de las redes de la asociación lo "
                  "que nos indiques, aunque no podemos recuperar lo que otras personas hayan copiado antes. Junto a la imagen de una "
                  "persona menor nunca publicamos su nombre completo ni otros datos que la identifiquen.",
            h3="3. Si es menor de 18 años: madre, padre o tutor/a", gname="Nombre y apellidos", gid="DNI / NIE / pasaporte",
            sign=("Firma de la persona socia (desde los 14 años)", "Firma de madre, padre o tutor/a (si es menor de 18)"),
            place="Lugar", date="Fecha",
            purpose=["Finalidad: difundir las actividades de la asociación con imágenes, solo en los usos marcados.",
                     "Base jurídica: tu consentimiento (RGPD art. 6.1.a; Ley Orgánica 1/1982, del derecho a la propia imagen; para "
                     "menores de 14 años, LOPDGDD art. 7).",
                     "Destinatarios: las imágenes publicadas son públicas; las redes sociales son de empresas que pueden tratar los datos "
                     "fuera de la UE, con las garantías que explica nuestra política de privacidad."]),
        "ca": dict(
            title="Autorització d'ús d'imatge",
            sub="Voluntària, una per persona. No donar-la no canvia res de la teva quota ni de les teves classes, i la pots retirar "
                "o canviar quan vulguis escrivint a info@aikidomusubi.com.",
            h1="1. La persona sòcia", name="Nom i cognoms",
            h2="2. Fotos i vídeos",
            intro="A les classes, els cursos, els exàmens i els esdeveniments fem fotografies i vídeos. Marca el que autoritzes; "
                  "pots marcar diverses opcions, o només l'última.",
            opts=["Ús intern: l'arxiu de l'associació i els grups de missatgeria de socis, no públics.",
                  "El web de l'associació (aikidomusubi.com).",
                  "Les xarxes socials de l'associació (Instagram, Facebook, YouTube).",
                  "Material imprès de difusió: cartells i fullets."],
            no="No autoritzo l'ús de la meva imatge, o de la de la persona menor.",
            terms="L'autorització és gratuïta i no té termini. Si la retires, traiem del web i de les xarxes de l'associació el que "
                  "ens indiquis, tot i que no podem recuperar el que altres persones hagin copiat abans. Al costat de la imatge d'una "
                  "persona menor no publiquem mai el seu nom complet ni altres dades que la identifiquin.",
            h3="3. Si és menor de 18 anys: mare, pare o tutor/a", gname="Nom i cognoms", gid="DNI / NIE / passaport",
            sign=("Signatura de la persona sòcia (des dels 14 anys)", "Signatura de la mare, el pare o el tutor/a (si és menor de 18)"),
            place="Lloc", date="Data",
            purpose=["Finalitat: difondre les activitats de l'associació amb imatges, només en els usos marcats.",
                     "Base jurídica: el teu consentiment (RGPD art. 6.1.a; Llei orgànica 1/1982, del dret a la pròpia imatge; per als "
                     "menors de 14 anys, LOPDGDD art. 7).",
                     "Destinataris: les imatges publicades són públiques; les xarxes socials són d'empreses que poden tractar les dades "
                     "fora de la UE, amb les garanties que explica la nostra política de privadesa."]),
        "en": dict(
            title="Image release",
            sub="Voluntary, one per person. Not giving it changes nothing about your membership or your classes, and you can withdraw "
                "or change it at any time by writing to info@aikidomusubi.com.",
            h1="1. The member", name="Full name",
            h2="2. Photos and videos",
            intro="We take photographs and videos at classes, courses, gradings and events. Tick what you agree to; you may tick "
                  "several options, or only the last one.",
            opts=["Internal use: the association's archive and the members' messaging groups, not public.",
                  "The association's website (aikidomusubi.com).",
                  "The association's social media (Instagram, Facebook, YouTube).",
                  "Printed publicity: posters and leaflets."],
            no="I do not agree to the use of my image, or of the minor's.",
            terms="The release is free and has no end date. If you withdraw it, we take down from the association's website and "
                  "social media whatever you tell us, though we cannot recover what others may already have copied. We never publish a "
                  "minor's full name or anything else that identifies them next to their picture.",
            h3="3. If under 18: parent or guardian", gname="Full name", gid="DNI / NIE / passport",
            sign=("Signature of the member (from age 14)", "Signature of a parent or guardian (if under 18)"),
            place="Place", date="Date",
            purpose=["Purpose: to show the association's activities with pictures, only in the uses ticked.",
                     "Legal basis: your consent (GDPR art. 6.1.a; Spanish Organic Law 1/1982 on the right to one's own image; for "
                     "children under 14, LOPDGDD art. 7).",
                     "Recipients: published pictures are public; social media belong to companies that may process data outside the EU, "
                     "with the safeguards our privacy policy explains."]),
    }[lang]
    f = Form(os.path.join(OUT, f"{PFX}imagen-{lang}.pdf"), t["title"], lang, t["sub"])
    f.header(t["title"], t["sub"])
    f.h(t["h1"])
    f.fields((t["name"], 1, "member_name"))
    f.h(t["h2"])
    f.para(t["intro"], color=BLACK)
    for i, o in enumerate(t["opts"]):
        f.check(f"use_{i + 1}", o)
    f.check("use_none", t["no"], bold=True)
    f.y -= 1 * mm
    f.para(t["terms"], size=7.6, color=INK)
    f.h(t["h3"])
    f.fields((t["gname"], 2, "guardian_name"), (t["gid"], 1, "guardian_id"))
    f.signatures(*t["sign"], place_label=t["place"], date_label=t["date"])
    head, common = LEGAL_COMMON[lang]
    f.legal(head, [common[0]] + t["purpose"] + [common[1]])
    f.save()


def minors(lang):
    t = {
        "es": dict(
            title="Autorización para menores",
            sub="Para cada socio o socia menor de 18 años, como piden los estatutos de la asociación (art. 4). La firman la madre, "
                "el padre o quien tenga la tutela.",
            h1="1. La persona menor", given="Nombre", family="Apellidos", born="Fecha de nacimiento (dd/mm/aaaa)",
            h2="2. Madre, padre o tutor/a", gname="Nombre y apellidos", gid="DNI / NIE / pasaporte", grel="Relación (madre, padre, tutor/a)",
            gphone="Teléfono", gemail="Correo electrónico",
            h2b="Segunda persona de contacto (opcional)",
            h3="3. Autorizo",
            c1="Que la persona menor sea socia de la asociación y participe en sus clases y actividades, y, si es menor de 14 años, "
               "el tratamiento de sus datos personales con ese fin.",
            c2="Que, en caso de urgencia y si no se me puede localizar, se avise a los servicios de emergencia y se la acompañe "
               "al centro sanitario.",
            c3="Que salga sola al acabar la clase. Si no marcas esta casilla, la recogeremos con una persona adulta autorizada.",
            pickup="Otras personas adultas autorizadas a recogerla (nombre y teléfono)",
            sign=("Firma de madre, padre o tutor/a",), place="Lugar", date="Fecha",
            purpose=["Finalidad: la participación de la persona menor en la asociación, las comunicaciones con su familia y la atención "
                     "en caso de urgencia.",
                     "Base jurídica: la relación asociativa (RGPD art. 6.1.b) y, para menores de 14 años, este consentimiento (LOPDGDD art. 7)."]),
        "ca": dict(
            title="Autorització per a menors",
            sub="Per a cada soci o sòcia menor de 18 anys, com demanen els estatuts de l'associació (art. 4). La signen la mare, "
                "el pare o qui en tingui la tutela.",
            h1="1. La persona menor", given="Nom", family="Cognoms", born="Data de naixement (dd/mm/aaaa)",
            h2="2. Mare, pare o tutor/a", gname="Nom i cognoms", gid="DNI / NIE / passaport", grel="Relació (mare, pare, tutor/a)",
            gphone="Telèfon", gemail="Correu electrònic",
            h2b="Segona persona de contacte (opcional)",
            h3="3. Autoritzo",
            c1="Que la persona menor sigui sòcia de l'associació i participi en les seves classes i activitats, i, si és menor de "
               "14 anys, el tractament de les seves dades personals amb aquesta finalitat.",
            c2="Que, en cas d'urgència i si no se'm pot localitzar, s'avisi els serveis d'emergència i se l'acompanyi al centre sanitari.",
            c3="Que surti sola en acabar la classe. Si no marques aquesta casella, la recollirem amb una persona adulta autoritzada.",
            pickup="Altres persones adultes autoritzades a recollir-la (nom i telèfon)",
            sign=("Signatura de la mare, el pare o el tutor/a",), place="Lloc", date="Data",
            purpose=["Finalitat: la participació de la persona menor a l'associació, les comunicacions amb la seva família i l'atenció "
                     "en cas d'urgència.",
                     "Base jurídica: la relació associativa (RGPD art. 6.1.b) i, per als menors de 14 anys, aquest consentiment (LOPDGDD art. 7)."]),
        "en": dict(
            title="Consent for minors",
            sub="For every member under 18, as the association's statutes require (art. 4). Signed by a parent or legal guardian.",
            h1="1. The minor", given="First name", family="Surnames", born="Date of birth (dd/mm/yyyy)",
            h2="2. Parent or guardian", gname="Full name", gid="DNI / NIE / passport", grel="Relationship (mother, father, guardian)",
            gphone="Phone", gemail="Email",
            h2b="Second contact person (optional)",
            h3="3. I consent",
            c1="To the minor being a member of the association and taking part in its classes and activities, and, if they are "
               "under 14, to the processing of their personal data for that purpose.",
            c2="To the emergency services being called, and the minor being taken to a medical centre, in an emergency when I "
               "cannot be reached.",
            c3="To the minor leaving on their own after class. If you do not tick this, we will hand them over to an authorised adult.",
            pickup="Other adults authorised to collect them (name and phone)",
            sign=("Signature of a parent or guardian",), place="Place", date="Date",
            purpose=["Purpose: the minor's participation in the association, communication with their family, and care in an emergency.",
                     "Legal basis: membership (GDPR art. 6.1.b) and, for children under 14, this consent (LOPDGDD art. 7)."]),
    }[lang]
    f = Form(os.path.join(OUT, f"{PFX}menores-{lang}.pdf"), t["title"], lang, t["sub"])
    f.header(t["title"], t["sub"])
    f.h(t["h1"])
    f.fields((t["given"], 1, "minor_given"), (t["family"], 2, "minor_family"), (t["born"], 1.3, "minor_born"))
    f.h(t["h2"])
    f.fields((t["gname"], 2, "g1_name"), (t["gid"], 1, "g1_id"))
    f.fields((t["grel"], 1, "g1_relation"), (t["gphone"], 1, "g1_phone"), (t["gemail"], 1.6, "g1_email"))
    f.y -= 4.5 * mm
    f.para(t["h2b"], size=7.8, color=BLACK, font="NotoBold")
    f.fields((t["gname"], 2, "g2_name"), (t["gphone"], 1, "g2_phone"), (t["grel"], 1.2, "g2_relation"))
    f.h(t["h3"])
    f.check("consent_membership", t["c1"])
    f.check("consent_emergency", t["c2"])
    f.check("consent_alone", t["c3"])
    f.fields((t["pickup"], 1, "pickup"))
    f.signatures(*t["sign"], place_label=t["place"], date_label=t["date"])
    head, common = LEGAL_COMMON[lang]
    f.legal(head, [common[0]] + t["purpose"] + [common[1]])
    f.save()


if __name__ == "__main__":
    faces()
    os.makedirs(OUT, exist_ok=True)
    for lang in ("es", "ca", "en"):
        for make in (enrolment, image, minors):
            make(lang)
    for name in sorted(os.listdir(OUT)):
        if name.startswith(PFX) and any(k in name for k in ("inscripcion", "imagen", "menores")):
            print(f"  files/{name:<44} {os.path.getsize(os.path.join(OUT, name)) / 1024:5.1f} KB")
