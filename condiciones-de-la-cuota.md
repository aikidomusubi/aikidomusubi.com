---
layout: membership
kind: terms
title: "Condiciones de la cuota"
seo_title: "Condiciones de la cuota: cobro, baja y desistimiento"
description: "Las condiciones de la cuota de entrenamiento: qué cubre, cómo y cuándo se cobra, cómo darse de baja, el derecho de desistimiento y los cambios de precio."
permalink: /condiciones-de-la-cuota/
lang: es
i18n-ref: membership-terms-Rb9vF6sJ
last_modified: 2026-10-14
no_analytics: true
review_pending: true
---
{%- assign MS = site.data.membership -%}
{%- assign FT = site.data.footer.ui -%}
{%- assign fam = site.data.fees.family.amount -%}
{%- assign fam_q = fam | times: 3 -%}
{%- assign fam_y = fam | times: 12 -%}

# Condiciones de la cuota

Versión {{ MS.terms_version }}, en vigor desde el 1 de enero de 2027. Son las condiciones que aceptas al inscribirte en línea. Te las enviamos también por correo al inscribirte.

{% if page.review_pending %}<p class="mb-draft">Borrador pendiente de la revisión del asesor legal.</p>{% endif %}

## 1. Quiénes somos

{{ FT.org }}, asociación sin ánimo de lucro con CIF {{ FT.cif }} y domicilio en {{ FT.address | replace: '<br>', ', ' }}. Correo: [info@aikidomusubi.com](mailto:info@aikidomusubi.com). Teléfono y WhatsApp: +34 717 171 177.

## 2. Qué cubre la cuota, y qué no

La **cuota general** da acceso a todas las clases de la asociación en todos sus espacios. La **cuota con abono municipal** da acceso solo a las clases del polideportivo cuyo abono tienes.

La cuota no incluye la licencia federativa y el seguro (apartado 13), los exámenes de dan, los seminarios y cursos, ni el keikogi, salvo el que regalamos con las cuotas trimestrales y anuales (apartado 14). Los exámenes de kyū no tienen coste.

## 3. Cuotas, descuento familiar y cuota con abono

Los importes de cada cuota, por edad y por periodo, son los publicados en [Cuotas]({{ MS.urls.fees.es }}) el día en que te inscribes, que forman parte de estas condiciones. Hay dos grupos de edad: hasta 16 años, y 17 años o más.

**Descuento familiar.** Una cuota puede incluir a varias personas del mismo núcleo familiar, con una sola persona titular que paga y un mismo periodo para todas. La primera persona paga la cuota completa y cada una de las siguientes, {{ fam }} € menos al mes ({{ fam_q }} € menos al trimestre, {{ fam_y }} € menos al año).

**Cuota con abono municipal.** Si tienes el abono del polideportivo de uno de nuestros espacios municipales, puedes pagar la cuota reducida de ese espacio, que cubre solo sus clases, se paga mes a mes y no se combina con el descuento familiar: quien la tiene ni recibe ni genera el descuento. Hay que enseñar el abono en la primera clase. Si no es válido, desde el siguiente cobro pasas a la cuota general y te avisamos por correo.

## 4. El cobro, el día 5

La cuota se cobra el día 5 de cada mes, de cada trimestre o de cada año, según el periodo que elijas. Al inscribirte pagas la parte proporcional de los días que faltan hasta el siguiente día 5; desde ese día, la cuota completa. Si te inscribes con una invitación del dojo, puede que el primer cobro sea directamente el día 5 que se indica en ella.

Pagas exactamente el importe publicado: no hay recargo por el medio de pago.

## 5. Medios de pago

Pagas con tarjeta o con domiciliación bancaria SEPA, en una página segura de Stripe, que procesa los pagos por cuenta de la asociación. La asociación no ve ni guarda los datos de tu tarjeta ni de tu cuenta. Con domiciliación, Stripe te avisa antes de cada cargo.

Si un cobro no puede hacerse, lo reintentamos en los días siguientes y te avisamos. La cuota sigue activa mientras lo resolvemos contigo. Si quedara impagada después de avisarte, podríamos darla por terminada.

## 6. Duración y renovación

La cuota no tiene fecha de fin: se renueva sola al acabar cada periodo y se cobra el día 5. **Quince días antes de cada renovación te avisamos por correo** de la fecha, el importe y cómo darte de baja si no quieres continuar.

## 7. Baja

Puedes darte de baja cuando quieras, sin penalización, en tu [área de miembros]({{ MS.urls.members.es }}), por correo, por teléfono o en el dojo. La baja se aplica al final del periodo ya pagado: hasta entonces puedes seguir entrenando, y no habrá más cobros. Te confirmamos la baja por correo.

## 8. Devoluciones

No se devuelve la parte no usada de un periodo pagado, sea mensual, trimestral o anual, salvo cuando ejerces el derecho de desistimiento (apartado 12).

## 9. Cambios de personas o de periodo

Para añadir o quitar personas, o cambiar de periodo, escríbenos. El cambio se aplica desde el siguiente cobro, recalculando el descuento familiar, y te lo confirmamos por correo con los importes.

## 10. El paso a la cuota de 17 años o más

De quien está en el grupo de hasta 16 años guardamos solo el mes y el año de nacimiento. Pasa a la cuota de 17 años o más desde el primer cobro de un mes posterior al de su cumpleaños número 17. Te avisamos por correo cuando ocurre, y en ese momento borramos su fecha de nacimiento.

## 11. Cambios de precio

Si la asamblea aprueba nuevas cuotas, te avisamos por escrito **con al menos un mes de antelación**. Si no estás de acuerdo, puedes darte de baja antes de que se apliquen, sin coste.

## 12. Derecho de desistimiento

Puedes desistir de la cuota durante los **14 días naturales** siguientes al día en que te inscribes, sin dar explicaciones. La forma más sencilla es el formulario de [desistimiento]({{ MS.urls.withdrawal.es }}), que te devuelve un acuse con la fecha y la hora; también vale cualquier declaración clara por correo, por teléfono o en el dojo.

Al inscribirte nos pides expresamente empezar a entrenar enseguida, antes de que acaben esos 14 días. Por eso, si desistes, pagas solo la parte proporcional a los días transcurridos hasta que nos lo comunicas, y te devolvemos el resto **en 14 días como máximo**, por el mismo medio de pago.

**Modelo de formulario de desistimiento.** A la atención de {{ FT.org }}, {{ FT.address | replace: '<br>', ', ' }}, info@aikidomusubi.com: por la presente comunico que desisto de mi contrato de cuota de entrenamiento celebrado el [fecha]. Nombre, dirección, firma (solo si se envía en papel) y fecha.

## 13. Licencia federativa y seguro

Para entrenar es obligatorio el seguro deportivo, que va con la licencia federativa. Cuesta 45 € al año por persona, se paga en marzo, aparte de la cuota, y se tramita desde el dojo a través de Arashi Group. La licencia da derecho a examen.

## 14. El keikogi de regalo

Con una cuota trimestral o anual, cada persona recibe un keikogi en su primera inscripción. Lo entregamos en el dojo cuando se ha cobrado el primer trimestre o año completo y han pasado los 14 días de desistimiento. Es uno por persona: un cambio de periodo o una nueva inscripción no incluye otro, y no se cambia por dinero.

## 15. Personas menores de edad

Quien paga tiene que ser mayor de edad. Si en la cuota hay personas menores de 18 años, quien paga declara ser su madre, padre, tutora o tutor legal. La hoja de inscripción en papel, firmada por quien tiene la patria potestad o la tutela, sigue siendo necesaria.

## 16. Protección de datos

Cómo tratamos tus datos está en la [política de privacidad]({{ MS.urls.privacy.es }}).

## 17. Reclamaciones y contacto

Para cualquier duda o queja, escríbenos a [info@aikidomusubi.com](mailto:info@aikidomusubi.com) o llámanos al +34 717 171 177. Tienes a tu disposición hojas oficiales de queja, reclamación y denuncia en el dojo.

## 18. Ley aplicable

Estas condiciones se rigen por la ley española. Si eres consumidor, puedes acudir a los tribunales de tu domicilio.
