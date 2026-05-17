# ActaTrace — Gestión Blockchain

**Documento:** Arquitectura operativa de blockchain  
**Versión:** 1.0 · Mayo 2026  
**Clasificación:** Público técnico

---

## 1. Principio de diseño

ActaTrace usa blockchain como **capa de verificación inmutable**, no como base de datos principal.

La base de datos relacional conserva el estado operativo del sistema. Blockchain conserva evidencia criptográfica mínima para demostrar que un documento o evento existía en un momento determinado y que no fue alterado después de su registro.

> ActaTrace no guarda actas completas en blockchain. Guarda hashes y eventos críticos verificables.

---

## 2. Responsabilidad de cada capa

| Capa | Responsabilidad | Tecnología recomendada |
|---|---|---|
| Aplicación | Registro, validación, permisos, workflows y consulta | React / Next.js / FastAPI |
| Base de datos | Fuente operativa del sistema | PostgreSQL |
| Storage documental | Almacenamiento seguro de archivos originales | Object Storage privado |
| Blockchain | Evidencia inmutable de hashes y eventos críticos | Hyperledger Fabric para MVP |
| Portal ciudadano | Consulta pública de evidencia verificable | Web público sin registro |

La regla de arquitectura es simple:

- Si el sistema necesita operar, consultar, filtrar o corregir estados, debe usar PostgreSQL.
- Si el sistema necesita probar integridad, existencia temporal o no alteración posterior al registro, debe usar blockchain.

---

## 3. Qué se registra en blockchain

Blockchain debe almacenar únicamente datos mínimos y no sensibles:

| Dato | Se registra on-chain | Motivo |
|---|---:|---|
| Hash SHA-256 del documento | Sí | Verificar integridad del archivo |
| ID público o folio del acta | Sí | Permitir correlación verificable |
| Tipo de evento | Sí | Identificar registro, validación, inconsistencia o cierre |
| Timestamp del evento | Sí | Evidencia temporal |
| Hash del evento anterior | Opcional | Encadenar cadena de custodia |
| Transaction ID | Sí, generado por red | Prueba de inclusión |
| Documento PDF o imagen | No | Evitar exposición de documentos completos |
| Nombre de funcionarios | No | Datos personales |
| Credenciales o usuarios internos | No | Seguridad operacional |
| Observaciones sensibles | No | Minimización de datos |

Regla obligatoria: **no publicar datos personales en blockchain ni en el Portal Ciudadano**.

---

## 4. Flujo operativo de registro

1. Un usuario autorizado carga un acta en el sistema.
2. El backend valida formato, tamaño, permisos y metadatos mínimos.
3. El archivo original se guarda en storage privado.
4. El backend calcula el hash SHA-256 del archivo original.
5. PostgreSQL registra el acta con estado `PENDING_BLOCKCHAIN`.
6. Se crea un evento interno de auditoría.
7. Se encola un job para registrar el hash en blockchain.
8. El worker blockchain envía la transacción a la red.
9. Cuando la red confirma, PostgreSQL guarda `blockchain_tx`, `blockchain_block`, `timestamp_blockchain` y cambia el estado a `CONFIRMED_ON_CHAIN`.
10. El Portal Ciudadano muestra el hash, estado y referencia de transacción.

El registro blockchain debe ser asincrónico. La captura de actas no debe bloquearse por latencia o indisponibilidad temporal de la red.

---

## 5. Estados recomendados

| Estado | Significado | Acción del sistema |
|---|---|---|
| `DRAFT` | El acta aún no fue confirmada por el capturista | No generar registro público |
| `HASHED` | El hash fue calculado y guardado internamente | Crear evento de auditoría |
| `PENDING_BLOCKCHAIN` | El hash está en cola de registro | Mostrar pendiente |
| `SUBMITTED_TO_CHAIN` | La transacción fue enviada | Esperar confirmación |
| `CONFIRMED_ON_CHAIN` | La transacción fue confirmada | Publicar verificación completa |
| `CHAIN_FAILED` | Falló el envío o confirmación | Reintentar y alertar |
| `MISMATCH_DETECTED` | El documento no coincide con el hash esperado | Bloquear verificación como válida |

Un acta pendiente de blockchain no debe presentarse como verificada. Debe mostrarse claramente como “capturada, pendiente de confirmación”.

---

## 6. Manejo de fallas

Blockchain no debe ser un punto único de falla para la operación electoral.

Si la red blockchain está lenta o no disponible:

- El sistema debe seguir aceptando actas válidas.
- Los eventos quedan en cola con reintentos controlados.
- El dashboard institucional muestra alertas operativas.
- El Portal Ciudadano muestra estado pendiente, no confirmación falsa.
- Ningún evento debe perderse; cada intento debe quedar auditado.

Los workers deben ser idempotentes. Reintentar el mismo evento no debe generar registros duplicados inconsistentes.

---

## 7. Modelo MVP

Para el MVP, la opción recomendada es **Hyperledger Fabric permissioned**.

Motivos:

- Permite nodos institucionales y auditores autorizados.
- Evita publicar datos sensibles en redes abiertas.
- Permite control operativo y gobernanza de participantes.
- Es coherente con un sistema electoral institucional.

Limitación: Hyperledger Fabric no es una red pública abierta por defecto. Por eso, si se comunica como “verificación pública”, el sistema debe explicar que la ciudadanía verifica evidencia publicada por ActaTrace y referencias de red permissioned, no necesariamente una transacción pública estilo Ethereum.

---

## 8. Evolución recomendada

Para fortalecer la verificación pública independiente, una fase posterior puede agregar anclaje periódico en red pública.

Modelo recomendado:

1. Durante el día, ActaTrace registra hashes y eventos en Hyperledger Fabric.
2. Cada periodo definido, el sistema construye un Merkle tree con los hashes confirmados.
3. Publica el Merkle root en una red pública o mecanismo externo verificable.
4. El Portal Ciudadano permite comprobar que un hash forma parte de ese root.

Esto permite transparencia pública sin exponer documentos ni datos personales.

---

## 9. Límites que deben comunicarse

Blockchain garantiza integridad **desde el momento del registro digital**.

No garantiza por sí sola:

- Que el acta física original sea auténtica.
- Que el proceso previo de traslado haya sido correcto.
- Que la captura humana no tenga errores.
- Que una institución haya actuado correctamente fuera del sistema.

La interfaz ciudadana debe declarar este límite con claridad:

> La verificación blockchain confirma que el documento registrado no cambió después de su carga. La autenticidad del proceso físico previo depende de controles institucionales y cadena de custodia.

---

## 10. Criterios de aceptación

Una implementación blockchain de ActaTrace se considera correcta si:

- Ningún documento completo se guarda on-chain.
- Ningún dato personal se guarda on-chain.
- Cada acta tiene hash SHA-256 reproducible.
- Cada evento crítico tiene bitácora interna.
- La confirmación blockchain se procesa de forma asincrónica.
- Los estados pendientes, confirmados y fallidos son visibles.
- El sistema puede operar aunque blockchain esté temporalmente indisponible.
- La ciudadanía puede verificar hash, estado y referencia de transacción cuando exista confirmación.
- La interfaz explica con precisión qué garantiza y qué no garantiza blockchain.

