---
layout: membership
kind: terms
title: "Condicions de la quota"
seo_title: "Condicions de la quota: cobrament, baixa i desistiment"
description: "Les condicions de la quota d'entrenament: què cobreix, com i quan es cobra, com donar-se de baixa, el dret de desistiment i els canvis de preu."
permalink: /ca/condicions-de-la-quota/
lang: ca
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

# Condicions de la quota

Versió {{ MS.terms_version }}, en vigor des de l'1 de gener de 2027. Són les condicions que acceptes en inscriure't en línia. També te les enviem per correu en inscriure't.

{% if page.review_pending %}<p class="mb-draft">Esborrany pendent de la revisió de l'assessor legal.</p>{% endif %}

## 1. Qui som, i què és ser soci o sòcia

{{ FT.org }}, associació sense ànim de lucre amb CIF {{ FT.cif }}, inscrita al Registre d'associacions de la Generalitat de Catalunya (secció 1a, Barcelona) amb el número {{ FT.registry }}, i amb domicili a {{ FT.address | replace: '<br>', ', ' }}. Correu: [info@aikidomusubi.com](mailto:info@aikidomusubi.com). Telèfon i WhatsApp: +34 717 171 177.

En inscriure't **sol·licites ser soci o sòcia** de l'associació, per tu i per cada persona que inscrius. Ser soci dona els drets i els deures que fixen els [estatuts](/ca/estatuts/): entre d'altres, participar amb veu i vot a l'assemblea general, i contribuir a sostenir l'associació amb la quota. Les quotes les aprova l'assemblea general, a proposta de la junta directiva.

La junta directiva admet les inscripcions. Si en la seva primera reunió no admetés alguna persona, et retornaríem íntegre el que haguessis pagat per ella.

## 2. Què cobreix la quota, i què no

La **quota general** dona accés a totes les classes de l'associació a tots els seus espais. La **quota amb abonament municipal** dona accés només a les classes del poliesportiu de què tens l'abonament.

La quota no inclou la llicència federativa i l'assegurança (apartat 13), els exàmens de dan, els seminaris i cursos, ni el keikogi, tret del que regalem amb les quotes trimestrals i anuals (apartat 14). Els exàmens de kyū no tenen cost.

## 3. Quotes, descompte familiar i quota amb abonament

Els imports de cada quota, per edat i per període, són els publicats a [Quotes]({{ MS.urls.fees.ca }}) el dia que t'inscrius, que formen part d'aquestes condicions. Hi ha dos grups d'edat: fins a 16 anys, i 17 anys o més.

**Descompte familiar.** Una quota pot incloure diverses persones del mateix nucli familiar, amb una sola persona titular que paga i un mateix període per a totes. La primera persona paga la quota completa i cadascuna de les següents, {{ fam }} € menys al mes ({{ fam_q }} € menys al trimestre, {{ fam_y }} € menys l'any).

**Quota amb abonament municipal.** Si tens l'abonament del poliesportiu d'un dels nostres espais municipals, pots pagar la quota reduïda d'aquell espai, que cobreix només les seves classes, es paga mes a mes i no es combina amb el descompte familiar: qui la té ni rep ni genera el descompte. Cal ensenyar l'abonament a la primera classe. Si no és vàlid, des del cobrament següent passes a la quota general i t'avisem per correu.

## 4. El cobrament, el dia 5

La quota es cobra el dia 5 de cada mes, de cada trimestre o de cada any, segons el període que triïs. En inscriure't pagues la part proporcional dels dies que falten fins al dia 5 següent; des d'aquell dia, la quota completa. Si t'inscrius amb una invitació del dojo, pot ser que el primer cobrament sigui directament el dia 5 que s'hi indica.

Pagues exactament l'import publicat: no hi ha recàrrec pel mitjà de pagament.

## 5. Mitjans de pagament

Pagues amb targeta o amb domiciliació bancària SEPA, en una pàgina segura de Stripe, que processa els pagaments per compte de l'associació. L'associació no veu ni guarda les dades de la teva targeta ni del teu compte. Amb domiciliació, Stripe t'avisa abans de cada càrrec.

Si un cobrament no es pot fer, el tornem a intentar els dies següents i t'avisem. La quota segueix activa mentre ho resolem amb tu. Si quedés impagada després d'avisar-te, la podríem donar per acabada.

## 6. Durada i renovació

La quota no té data de fi: es renova sola en acabar cada període i es cobra el dia 5. **Quinze dies abans de cada renovació t'avisem per correu** de la data, l'import i com donar-te de baixa si no vols continuar.

## 7. Baixa

Et pots donar de baixa quan vulguis, **sense penalització ni cost**. El més senzill és fer-ho tu, a la teva [àrea de membres]({{ MS.urls.members.ca }}): hi entres amb el teu correu i un codi, prems «Cancel·lar» i ho confirmes, i queda registrat al moment. També ens pots escriure a [info@aikidomusubi.com](mailto:info@aikidomusubi.com) o demanar-ho al dojo, on ho deixem registrat per escrit. La baixa s'aplica al final del període ja pagat: fins aleshores pots continuar entrenant, i no hi haurà més cobraments. Te la confirmem per correu.

Amb una quota trimestral o anual, pots demanar a més que et retornem els mesos que no hagis començat (apartat 8).

Com preveuen els estatuts, també és causa de baixa no pagar la quota un cop t'hem avisat (apartat 5).

## 8. Devolucions

- **Quota mensual.** En donar-te de baixa no hi ha res a retornar: la baixa s'aplica al final del mes ja pagat.
- **Quota trimestral o anual.** Si et dones de baixa abans que acabi el trimestre o l'any, ens pots demanar que et retornem els mesos que encara no hagis començat, sense donar explicacions. Ho calculem com si haguessis pagat mes a mes: al que vas pagar per aquell període li restem la quota mensual vigent de cada mes ja començat, amb el descompte familiar si el tens. Per exemple, amb una quota anual de 17 anys o més, si et dones de baixa el quart mes de l'any et retornem 360 € − 4 × 39 € = 204 €. Si el resultat és zero o menys, no hi ha devolució. La quota acaba el dia que ho demanes, i et retornem l'import en 14 dies com a màxim, pel mateix mitjà de pagament. Si ja t'hem lliurat el keikogi de regal (apartat 14), també descomptem el que ens va costar, {{ kc.adults }} € el d'adult i {{ kc.children }} € l'infantil: el vam comprar per a tu i no es pot retornar, així que te'l quedes.
- **Si és l'associació qui acaba la teva quota**, per una causa que no sigui l'impagament, o si deixa de fer les classes que la teva quota cobreix, et retornem la part del període pagat que no hagis pogut fer servir.
- **Desistiment**, durant els 14 dies següents a la inscripció: apartat 12.

## 9. Canvis de persones o de període

Per afegir o treure persones, o canviar de període, escriu-nos. El canvi s'aplica des del cobrament següent, recalculant el descompte familiar, i te'l confirmem per correu amb els imports.

## 10. El pas a la quota de 17 anys o més

De qui és al grup de fins a 16 anys guardem només el mes i l'any de naixement. Passa a la quota de 17 anys o més des del primer cobrament d'un mes posterior al del seu aniversari número 17. T'avisem per correu quan passa, i en aquell moment esborrem la seva data de naixement.

## 11. Canvis de preu

Si l'assemblea aprova noves quotes, t'avisem per escrit **amb almenys un mes d'antelació**. Si no hi estàs d'acord, et pots donar de baixa abans que s'apliquin, sense cost.

## 12. Dret de desistiment

Tens dret a desistir de la quota en un termini de **14 dies naturals** des del dia que t'inscrius, sense necessitat de justificació.

Per exercir-lo, comunica-ho amb una declaració inequívoca. La manera més senzilla és el formulari de [desistiment]({{ MS.urls.withdrawal.ca }}), que t'envia un justificant amb la data i l'hora; també serveix un correu a [info@aikidomusubi.com](mailto:info@aikidomusubi.com), una carta al nostre domicili o dir-nos-ho al dojo. Pots fer servir el model de formulari de sota, tot i que no és obligatori. Per complir el termini, n'hi ha prou que ens ho comuniquis abans que acabin els 14 dies.

En inscriure't ens demanes expressament començar a entrenar de seguida, abans que acabi aquest termini. Per això, si desisteixes, ens abones un import proporcional a la part ja prestada fins al moment en què ens ho comuniques, calculat per dies, i et retornem la resta sense demora i **en 14 dies naturals com a màxim** des d'aquell moment. Ho fem pel mateix mitjà de pagament que vas fer servir, tret que ens en demanis expressament un altre, i la devolució no et suposa cap despesa. La quota acaba en aquell moment i no hi haurà més cobraments.

**Model de formulari de desistiment** (només l'has d'emplenar i enviar si vols desistir del contracte):

> A l'atenció de {{ FT.org }}, {{ FT.address | replace: '<br>', ', ' }}, info@aikidomusubi.com:
>
> Per la present li comunico/comuniquem (\*) que desisteixo del meu/desistim del nostre (\*) contracte de prestació del servei següent: quota d'entrenament.
>
> Contractat el (\*):
>
> Nom del consumidor o dels consumidors:
>
> Domicili del consumidor o dels consumidors:
>
> Signatura del consumidor o dels consumidors (només si aquest formulari es presenta en paper):
>
> Data:
>
> (\*) Ratlleu el que no correspongui.

## 13. Llicència federativa i assegurança

Per entrenar és obligatòria l'assegurança esportiva, que va amb la llicència federativa. Costa 45 € l'any per persona, es paga al març, a part de la quota, i es tramita des del dojo a través d'Arashi Group. La llicència dona dret a examen.

## 14. El keikogi de regal

Amb una quota trimestral o anual, cada persona rep un keikogi en la seva primera inscripció. El lliurem al dojo quan s'ha cobrat el primer trimestre o any complet i han passat els 14 dies de desistiment. És un per persona: un canvi de període o una nova inscripció no n'inclou un altre, i no es canvia per diners. Si deixes la quota abans d'hora i demanes la devolució dels mesos no començats, es descompta el que va costar (apartat 8).

## 15. Persones menors d'edat, i imatges

Qui paga ha de ser major d'edat. Si a la quota hi ha persones menors de 18 anys, qui paga declara ser-ne la mare, el pare, la tutora o el tutor legal, i dona el seu consentiment perquè siguin sòcies, com demanen els estatuts; per als menors de 14 anys, aquest consentiment cobreix també el tractament de les seves dades. Continua sent necessari el full d'inscripció en paper, signat per qui té la pàtria potestat o la tutela.

**Fotos i vídeos.** A les classes, els cursos i els esdeveniments fem fotos i vídeos. Publicar al web o a les xarxes socials imatges en què se't reconegui requereix el teu consentiment per escrit, o el de la mare, el pare o el tutor si ets menor, en una autorització a part que et donem al dojo. És voluntària: no donar-la no canvia res de la teva quota, i la pots retirar quan vulguis amb un correu.

## 16. Protecció de dades

Com tractem les teves dades és a la [política de privadesa]({{ MS.urls.privacy.ca }}).

## 17. Reclamacions i contacte

Per a qualsevol dubte, queixa o reclamació, escriu-nos a [info@aikidomusubi.com](mailto:info@aikidomusubi.com) o truca'ns al +34 717 171 177; et responem en un mes com a màxim. Al dojo tens a la teva disposició fulls oficials de queixa, reclamació i denúncia. També et pots adreçar a l'Agència Catalana del Consum o a l'oficina d'informació al consumidor del teu ajuntament. L'associació no està adherida al sistema arbitral de consum.

## 18. Llei aplicable

Aquestes condicions es regeixen per la llei espanyola. Si ets consumidor, pots acudir als tribunals del teu domicili.
