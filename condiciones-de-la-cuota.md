---
layout: membership
kind: terms
title: "Condiciones de la cuota"
seo_title: "Condiciones de la cuota: cobro, baja y desistimiento"
description: "Las condiciones de la cuota de entrenamiento: qué cubre, cómo y cuándo se cobra, cómo darse de baja, el derecho de desistimiento y los cambios de precio."
permalink: /condiciones-de-la-cuota/
lang: es
i18n-ref: membership-terms-Rb9vF6sJ
last_modified: 2026-10-15
no_analytics: true
review_pending: true
---
{%- assign MS = site.data.membership -%}
{%- assign FT = site.data.footer.ui -%}
{%- assign fam = site.data.fees.family.amount -%}
{%- assign kc = site.data.fees.offer.cost -%}
{%- assign fam_q = fam | times: 3 -%}
{%- assign fam_y = fam | times: 12 -%}

# Condiciones de la cuota

Versión {{ MS.terms_version }}, en vigor desde el 1 de enero de 2027. Son las condiciones que aceptas al inscribirte en línea. Te las enviamos también por correo al inscribirte.

{% if page.review_pending %}<p class="mb-draft">Borrador pendiente de la revisión del asesor legal.</p>{% endif %}

## 1. Quiénes somos, y qué es ser socio o socia

{{ FT.org }}, asociación sin ánimo de lucro con CIF {{ FT.cif }}, inscrita en el Registro de Asociaciones de la Generalitat de Catalunya (sección 1.ª, Barcelona) con el número {{ FT.registry }}, y con domicilio en {{ FT.address | replace: '<br>', ', ' }}. Correo: [info@aikidomusubi.com](mailto:info@aikidomusubi.com). Teléfono y WhatsApp: +34 717 171 177.

Al inscribirte **solicitas ser socio o socia** de la asociación, por ti y por cada persona que inscribes. Ser socio da los derechos y los deberes que fijan los [estatutos](/ca/estatuts/), que están en catalán: entre ellos, participar con voz y voto en la asamblea general, y contribuir a sostener la asociación con la cuota. Las cuotas las aprueba la asamblea general, a propuesta de la junta directiva.

La junta directiva admite las inscripciones. Si en su primera reunión no admitiera a alguna persona, te devolveríamos íntegro lo que hubieras pagado por ella.

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

Puedes darte de baja cuando quieras, **sin penalización ni coste**. Lo más sencillo es hacerlo tú, en tu [área de miembros]({{ MS.urls.members.es }}): entras con tu correo y un código, pulsas «Cancelar» y lo confirmas, y queda registrado al momento. También puedes escribirnos a [info@aikidomusubi.com](mailto:info@aikidomusubi.com) o pedirlo en el dojo, donde lo dejamos registrado por escrito. La baja se aplica al final del periodo ya pagado: hasta entonces puedes seguir entrenando, y no habrá más cobros. Te la confirmamos por correo.

Con una cuota trimestral o anual, puedes pedir además que te devolvamos los meses que no hayas empezado (apartado 8).

Como prevén los estatutos, también es causa de baja no pagar la cuota una vez que te hemos avisado (apartado 5).

## 8. Devoluciones

- **Cuota mensual.** Al darte de baja no hay nada que devolver: la baja se aplica al final del mes ya pagado.
- **Cuota trimestral o anual.** Si te das de baja antes de que acabe el trimestre o el año, puedes pedirnos que te devolvamos los meses que aún no hayas empezado, sin dar explicaciones. Lo calculamos como si hubieras pagado mes a mes: a lo que pagaste por ese periodo le restamos la cuota mensual vigente de cada mes ya empezado, con el descuento familiar si lo tienes. Por ejemplo, con una cuota anual de 17 años o más, si te das de baja en el cuarto mes del año te devolvemos 360 € − 4 × 39 € = 204 €. Si el resultado es cero o menos, no hay devolución. La cuota termina el día en que lo pides, y te devolvemos el importe en 14 días como máximo, por el mismo medio de pago. Si ya te hemos entregado el keikogi de regalo (apartado 14), descontamos también lo que nos costó, {{ kc.adults }} € el de adulto y {{ kc.children }} € el infantil: lo compramos para ti y no se puede devolver, así que te lo quedas.
- **Si es la asociación quien termina tu cuota**, por una causa que no sea el impago, o si deja de dar las clases que tu cuota cubre, te devolvemos la parte del periodo pagado que no hayas podido usar.
- **Desistimiento**, durante los 14 días siguientes a la inscripción: apartado 12.

## 9. Cambios de personas o de periodo

Para añadir o quitar personas, o cambiar de periodo, escríbenos. El cambio se aplica desde el siguiente cobro, recalculando el descuento familiar, y te lo confirmamos por correo con los importes.

## 10. El paso a la cuota de 17 años o más

De quien está en el grupo de hasta 16 años guardamos solo el mes y el año de nacimiento. Pasa a la cuota de 17 años o más desde el primer cobro de un mes posterior al de su cumpleaños número 17. Te avisamos por correo cuando ocurre, y en ese momento borramos su fecha de nacimiento.

## 11. Cambios de precio

Si la asamblea aprueba nuevas cuotas, te avisamos por escrito **con al menos un mes de antelación**. Si no estás de acuerdo, puedes darte de baja antes de que se apliquen, sin coste.

## 12. Derecho de desistimiento

Tienes derecho a desistir de la cuota en un plazo de **14 días naturales** desde el día en que te inscribes, sin necesidad de justificación.

Para ejercerlo, comunícanoslo con una declaración inequívoca. La forma más sencilla es el formulario de [desistimiento]({{ MS.urls.withdrawal.es }}), que te envía un acuse con la fecha y la hora; también vale un correo a [info@aikidomusubi.com](mailto:info@aikidomusubi.com), una carta a nuestro domicilio o decírnoslo en el dojo. Puedes usar el modelo de formulario de abajo, aunque no es obligatorio. Para cumplir el plazo, basta con que nos lo comuniques antes de que acaben los 14 días.

Al inscribirte nos pides expresamente empezar a entrenar enseguida, antes de que acabe ese plazo. Por eso, si desistes, nos abonas un importe proporcional a la parte ya prestada hasta el momento en que nos lo comunicas, calculado por días, y te devolvemos el resto sin demora y **en 14 días naturales como máximo** desde ese momento. Lo hacemos por el mismo medio de pago que usaste, salvo que nos pidas expresamente otro, y la devolución no te supone ningún gasto. La cuota termina en ese momento y no habrá más cobros.

**Modelo de formulario de desistimiento** (solo tienes que rellenarlo y enviarlo si quieres desistir del contrato):

> A la atención de {{ FT.org }}, {{ FT.address | replace: '<br>', ', ' }}, info@aikidomusubi.com:
>
> Por la presente le comunico/comunicamos (\*) que desisto de mi/desistimos de nuestro (\*) contrato de prestación del siguiente servicio: cuota de entrenamiento.
>
> Contratado el (\*):
>
> Nombre del consumidor o de los consumidores:
>
> Domicilio del consumidor o de los consumidores:
>
> Firma del consumidor o de los consumidores (solo si el presente formulario se presenta en papel):
>
> Fecha:
>
> (\*) Táchese lo que no proceda.

## 13. Licencia federativa y seguro

Para entrenar es obligatorio el seguro deportivo, que va con la licencia federativa. Cuesta 45 € al año por persona, se paga en marzo, aparte de la cuota, y se tramita desde el dojo a través de Arashi Group. La licencia da derecho a examen.

## 14. El keikogi de regalo

Con una cuota trimestral o anual, cada persona recibe un keikogi en su primera inscripción. Lo entregamos en el dojo cuando se ha cobrado el primer trimestre o año completo y han pasado los 14 días de desistimiento. Es uno por persona: un cambio de periodo o una nueva inscripción no incluye otro, y no se cambia por dinero. Si dejas la cuota antes de tiempo y pides la devolución de los meses no empezados, se descuenta lo que costó (apartado 8).

## 15. Personas menores de edad, e imágenes

Quien paga tiene que ser mayor de edad. Si en la cuota hay personas menores de 18 años, quien paga declara ser su madre, padre, tutora o tutor legal, y da su consentimiento para que sean socias, como piden los estatutos; para menores de 14 años, ese consentimiento cubre también el tratamiento de sus datos. La hoja de inscripción en papel, firmada por quien tiene la patria potestad o la tutela, sigue siendo necesaria.

**Fotos y vídeos.** En clases, cursos y eventos hacemos fotos y vídeos. Publicar en la web o en redes sociales imágenes en las que se te reconozca requiere tu consentimiento por escrito, o el de madre, padre o tutor si eres menor, en una autorización aparte que te damos en el dojo. Es voluntaria: no darla no cambia nada de tu cuota, y puedes retirarla cuando quieras con un correo.

## 16. Protección de datos

Cómo tratamos tus datos está en la [política de privacidad]({{ MS.urls.privacy.es }}).

## 17. Reclamaciones y contacto

Para cualquier duda, queja o reclamación, escríbenos a [info@aikidomusubi.com](mailto:info@aikidomusubi.com) o llámanos al +34 717 171 177; te contestamos en un mes como máximo. En el dojo tienes a tu disposición hojas oficiales de queja, reclamación y denuncia. También puedes dirigirte a la Agència Catalana del Consum o a la oficina de información al consumidor de tu ayuntamiento. La asociación no está adherida al sistema arbitral de consumo.

## 18. Ley aplicable

Estas condiciones se rigen por la ley española. Si eres consumidor, puedes acudir a los tribunales de tu domicilio.
