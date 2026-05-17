# ActaTrace — Script de Pitch Narrado

**Duración objetivo:** 3 minutos 30 segundos  
**Audiencia:** Inversionistas GovTech / Aceleradoras  
**Tono:** Directo, técnico, sin dramatismo innecesario. Confianza, no urgencia fabricada.

> **Nota de presentación:** Las pausas marcadas con `[PAUSA]` son intencionadas. No las saltes. El silencio en los puntos de datos da tiempo al público para absorber. Habla al ritmo normal de conversación, no de presentación.

---

## SLIDE 1 — APERTURA [0:00 – 0:25]

En México, cada proceso electoral produce más de 170,000 actas físicas.

Cada acta contiene el resultado de una casilla.

Esas actas son la fuente de verdad del proceso democrático.

`[PAUSA 2s]`

Ningún ciudadano puede verificar si el resultado publicado en el PREP corresponde exactamente con lo que dice esa acta.

No porque la información sea secreta.

Sino porque no existe la infraestructura para hacerlo.

Eso es lo que construimos.

---

## SLIDE 2 — EL PROBLEMA [0:25 – 1:10]

El problema no es que las elecciones sean fraudulentas.

El problema es que no tenemos cómo probar que no lo son.

Tres hechos concretos:

**Primero:** El PREP no está vinculado con el acta que lo respalda. Los resultados se capturan. Nadie puede rastrear de cuál documento vienen.

**Segundo:** La cadena de custodia no existe como registro público. No sabemos quién tocó cada documento, en qué momento, ni si llegó intacto.

**Tercero:** Si hay una diferencia entre el acta y el PREP, solo se detecta si alguien lo busca manualmente.

`[PAUSA 2s]`

El 63% de los mexicanos desconfía de los resultados electorales.

No por evidencia de fraude.

Por falta de evidencia de lo contrario.

Ese es el problema que resolvemos.

---

## SLIDE 3 — LA SOLUCIÓN [1:10 – 1:55]

ActaTrace es una capa de trazabilidad y verificación sobre el proceso electoral.

No sustituye al INE. No es voto electrónico. No hay cripto.

El flujo es simple:

Una acta física se sube al sistema. El sistema genera automáticamente un hash SHA-256, que es la huella digital única de ese documento. Ese hash se registra en blockchain. Y desde ese momento, cualquier ciudadano puede verificar que el documento no fue alterado.

`[PAUSA 1s]`

Si el PREP dice 342 votos y el acta dice 342 votos, el sistema lo confirma.

Si hay diferencia, el sistema lo detecta automáticamente, lo registra como evento en la bitácora de auditoría, y lo hace visible en el portal público.

Sin que nadie tenga que buscarlo.

El MVP tiene cinco módulos: registro de actas, cadena de custodia, PREP verificable, bitácora de auditoría y portal ciudadano.

---

## SLIDE 4 — DEMO [1:55 – 2:30]

Déjame mostrarte cómo lo usa un ciudadano.

Entra al portal. Ingresa el número de su casilla.

Ve el resultado de su casilla. El número de votos en el acta. El número capturado en PREP. Si coinciden, un checkmark verde. Si hay diferencia, una alerta con evidencia.

Debajo, el hash SHA-256 del documento. Y la transacción en blockchain que lo registra.

`[PAUSA 1s]`

El punto clave es este: el ciudadano no necesita confiar en ActaTrace para verificar.

Puede tomar ese hash y confirmarlo directamente en la red blockchain.

El sistema es verificable sin depender del sistema.

Eso es lo que significa auditabilidad real.

---

## SLIDE 5 — IMPACTO [2:30 – 2:55]

El mercado inmediato es México: 18 procesos electorales estatales y federales en los próximos tres años.

El mercado regional es LATAM: 18 países con elecciones anuales, y actualmente cero soluciones de este tipo.

El modelo es B2G SaaS. Licencia anual por proceso electoral, entre 80 y 400 mil dólares dependiendo de la escala.

El mercado global de GovTech para integridad electoral está en 2.4 mil millones de dólares y creciendo.

No tenemos competencia directa en la región.

---

## SLIDE 6 — TECNOLOGÍA [2:55 – 3:15]

El stack es maduro y probado: FastAPI, PostgreSQL, React, Hyperledger Fabric.

La arquitectura está diseñada en cuatro capas desacopladas: interfaz, lógica, datos y verificación blockchain.

Blockchain solo almacena hashes y eventos críticos. Nunca datos personales. Nunca el documento completo.

La regla de diseño que usamos es simple: si no puedes auditarlo sin blockchain, el diseño está mal.

Estamos listos para auditoría gubernamental, revisión de medios y escrutinio técnico externo.

---

## SLIDE 7 — EL PEDIDO [3:15 – 3:30]

Buscamos 450,000 dólares seed.

Con eso financiamos 18 meses de desarrollo del equipo núcleo, la infraestructura de producción y un piloto con una autoridad electoral estatal en México.

El Q3 de este año tenemos capacidad de integración con un proceso real.

`[PAUSA 1s]`

ActaTrace no pide que confíen en el sistema.

Pide que lo verifiquen.

Eso es exactamente el punto.

`[PAUSA 2s]`

Gracias.

---

## Guía de tempo

| Sección | Tiempo | Slides |
|---|---|---|
| Apertura / contexto | 0:00 – 0:25 | 1 |
| El problema | 0:25 – 1:10 | 2 |
| La solución | 1:10 – 1:55 | 3 |
| Demo | 1:55 – 2:30 | 4 |
| Impacto y mercado | 2:30 – 2:55 | 5 |
| Tecnología | 2:55 – 3:15 | 6 |
| Cierre y ask | 3:15 – 3:30 | 7 |
| **Total** | **~3:30** | **7 slides** |

---

## Preguntas frecuentes esperadas (Q&A prep)

**¿Por qué blockchain y no solo una base de datos con hash?**  
Una base de datos centralizada puede ser modificada por el administrador. Blockchain garantiza que el registro de hash no puede ser alterado por ningún actor del sistema, incluyendo nosotros.

**¿Qué pasa si el acta se manipula antes de subirla?**  
ActaTrace garantiza la integridad del documento desde el momento del registro. La integridad del proceso físico previo depende de los controles institucionales. No lo resolvemos, pero lo declaramos explícitamente en la interfaz.

**¿Cómo se monetiza si el gobierno no paga software fácilmente?**  
El modelo es similar a GovTech establecidos como Palantir, Tyler Technologies o NIC Global. Licencia por proceso electoral con contrato plurianual. Además, fondos de transparencia internacional (OEA, BID, NDI) ya financian soluciones de este tipo.

**¿Tienen tracción?**  
Prototipo funcional completo. Arquitectura técnica definida. Marco legal validado. Buscamos el primer piloto institucional.

**¿Por qué ahora?**  
México tiene elecciones estatales en 2026 y elecciones federales en 2027. La ventana para un piloto real existe ahora.

---

*ActaTrace · Script v1.0 · Mayo 2026*  
*"Confianza no se declara. Se construye con evidencia verificable."*
