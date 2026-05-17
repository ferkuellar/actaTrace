# ActaTrace — Anclaje Normativo y Ético

**Documento:** Marco legal, derechos democráticos y consideraciones éticas  
**Versión:** 1.0 · Mayo 2026  
**Clasificación:** Público

---

## 1. Contexto del documento

Este documento identifica el marco normativo que sustenta el desarrollo y operación de ActaTrace como plataforma de trazabilidad electoral. Establece los fundamentos legales, los derechos democráticos que la plataforma protege y las consideraciones éticas que rigen su diseño.

> **Principio rector:** La tecnología no sustituye al marco legal. Lo hace verificable.

---

## 2. Marco Constitucional

### Artículo 41 — Constitución Política de los Estados Unidos Mexicanos (CPEUM)

Establece que las elecciones deben ser libres, auténticas y periódicas, con organismos electorales autónomos. ActaTrace contribuye a la **autenticidad** al garantizar que los resultados sean verificables y no alterados.

**Conexión directa:**
- Toda acta registrada en ActaTrace es trazable hasta su origen documental.
- La inmutabilidad blockchain refuerza la autenticidad del proceso.

### Artículo 6 — Derecho a la Información

Los ciudadanos tienen derecho a acceder a información pública. El Portal Ciudadano de ActaTrace materializa este derecho para los datos electorales verificables.

### Artículo 35 — Derechos Políticos

El voto es un derecho ciudadano cuya validez depende de la integridad del conteo. ActaTrace protege este derecho al hacer el proceso de conteo auditable de forma independiente.

---

## 3. Marco Electoral Federal

### Ley General de Instituciones y Procedimientos Electorales (LGIPE)

| Artículo | Disposición | Relación con ActaTrace |
|---|---|---|
| Art. 350 | Las actas electorales son documentos oficiales | ActaTrace registra y preserva el hash de cada acta como evidencia de integridad |
| Art. 354 | Los partidos y ciudadanos pueden solicitar recuentos | La cadena de custodia en ActaTrace hace los recuentos verificables en tiempo real |
| Art. 356 | El PREP debe reflejar resultados de actas físicas | El módulo PREP Verificable compara automáticamente y alerta diferencias |
| Art. 300 | Los observadores electorales tienen derecho de acceso | El rol OBSERVADOR en ActaTrace permite acceso de solo lectura sin restricción |

### Programa de Resultados Electorales Preliminares (PREP)

El PREP es un ejercicio de transparencia del INE. ActaTrace extiende su auditabilidad al:
- Vincular cada captura PREP con el acta fuente.
- Detectar automáticamente diferencias entre acta física y dato capturado.
- Registrar en blockchain la coincidencia o inconsistencia como evento inmutable.

---

## 4. Marco de Transparencia y Acceso a la Información

### Ley General de Transparencia y Acceso a la Información Pública

- Los resultados electorales son información pública de oficio.
- ActaTrace publica hashes y registros de verificación sin restricción de acceso.
- El Portal Ciudadano no requiere registro ni autenticación.

### Principio de máxima publicidad

Todo dato electoral verificable debe ser de acceso libre. ActaTrace no crea restricciones artificiales a la consulta pública de evidencia electoral.

---

## 5. Marco de Privacidad y Protección de Datos

### Ley Federal de Protección de Datos Personales en Posesión de Particulares (LFPDPPP)

ActaTrace maneja los siguientes tipos de datos y sus controles:

| Tipo de dato | Clasificación | Tratamiento en ActaTrace |
|---|---|---|
| Nombre de funcionarios de casilla | Dato personal | Almacenado en sistema, no publicado en portal ciudadano |
| Hash de documento | No personal | Público y publicado en blockchain |
| Resultado de casilla (votos agregados) | Dato público | Publicado en portal ciudadano |
| Credencial o identificador del capturista | Dato personal | Solo visible para SUPERVISOR y AUDITOR |
| Metadatos de transacción | Técnico | Público (blockchain es pública) |

**Regla de diseño:** ActaTrace no publica datos personales en blockchain ni en el Portal Ciudadano. Solo hashes y resultados agregados.

---

## 6. Marco Internacional de Referencia

### Declaración Universal de Derechos Humanos — Artículo 21

> "La voluntad del pueblo es la base de la autoridad del poder público; esta voluntad se expresará mediante elecciones auténticas."

ActaTrace hace verificable que los resultados correspondan a la voluntad expresada en actas físicas.

### Principios de la OEA para Elecciones Democráticas

- Transparencia del proceso electoral.
- Capacidad de auditoría independiente.
- Acceso a información por parte de observadores.

ActaTrace cumple los tres principios al nivel de la capa tecnológica de registro y verificación.

---

## 7. Consideraciones Éticas

### 7.1 Neutralidad tecnológica

ActaTrace no favorece a ningún partido, candidato ni resultado. El sistema registra evidencia. La interpretación es de los ciudadanos y las instituciones.

**Control:** El sistema no tiene lógica que clasifique resultados como "favorables" o "desfavorables". Solo detecta inconsistencias matemáticas.

### 7.2 No sustitución de la autoridad electoral

ActaTrace no pretende reemplazar al INE, los tribunales electorales ni los mecanismos legales de impugnación. Es una **capa adicional de evidencia**, no una autoridad.

**Control:** El sistema no tiene poder de anular, modificar ni invalidar resultados. Solo los registra y verifica.

### 7.3 Inclusión digital

El Portal Ciudadano está diseñado para ser accesible:
- Sin necesidad de cuenta ni registro.
- Con lenguaje comprensible para ciudadanos no técnicos.
- Con diseño responsivo para dispositivos móviles.
- Compatible con lectores de pantalla (WCAG 2.1 AA).

**Riesgo reconocido:** La brecha digital puede limitar el acceso a comunidades rurales o sin conectividad. ActaTrace no resuelve esta brecha pero no la amplía.

### 7.4 Riesgo de falsa certeza

La presencia de blockchain no garantiza que el acta original sea correcta. Solo garantiza que el documento no fue alterado **después** de su registro.

**Comunicación obligatoria:** El sistema muestra explícitamente este límite en la interfaz ciudadana. La integridad del proceso antes del registro depende de controles institucionales, no tecnológicos.

### 7.5 Transparencia del propio sistema

El código fuente de ActaTrace debe ser auditado o publicado como open source para que su funcionamiento sea verificable de forma independiente.

**Compromiso:** El sistema no puede ser confiable si él mismo no es transparente.

### 7.6 Gobernanza de claves privadas

Las claves de firma para los eventos en blockchain deben estar bajo custodia multi-firma, sin que ningún actor individual pueda comprometer la integridad del registro.

---

## 8. Mecanismos Democráticos Que Protege

| Mecanismo | Cómo ActaTrace lo fortalece |
|---|---|
| Conteo de votos | Hace trazable cada acta desde el origen hasta el resultado publicado |
| PREP | Vincula cada dato preliminar con su evidencia documental |
| Observación electoral | Permite a observadores verificar en tiempo real sin acceso privilegiado |
| Recuento | Proporciona evidencia de estado del documento en cada momento del proceso |
| Impugnaciones | Genera evidencia verificable de inconsistencias con timestamp y hash |
| Auditoría post-electoral | Preserva la bitácora completa con evidencia inmutable |

---

## 9. Lo que ActaTrace no es (límites éticos explícitos)

| Lo que NO hace | Razón |
|---|---|
| No decide si un resultado es válido | Eso es competencia del TEPJF |
| No identifica responsables de fraude | Eso es competencia del Ministerio Público |
| No certifica la identidad de funcionarios | Eso requiere verificación con el INE |
| No sustituye el recuento manual | El recuento físico es el mecanismo legal |
| No garantiza la integridad del proceso físico | Solo del registro digital posterior al upload |

---

## 10. Resumen de alineación

| Criterio | Estado |
|---|---|
| Fundamento constitucional | ✓ Art. 6, 35, 41 CPEUM |
| Marco electoral federal | ✓ LGIPE |
| Marco de transparencia | ✓ Ley General de Transparencia |
| Protección de datos personales | ✓ LFPDPPP con segregación de datos |
| Derechos de observación | ✓ Rol OBSERVADOR en sistema |
| Neutralidad política | ✓ No hay lógica de clasificación política |
| Inclusión digital | ✓ Portal público sin registro |
| Auditabilidad del propio sistema | ✓ Open source recomendado |

---

*Este documento debe revisarse con asesoría jurídica especializada en derecho electoral antes de implementación institucional.*

**ActaTrace · 2026 · "Confianza no se declara. Se construye con evidencia verificable."**
