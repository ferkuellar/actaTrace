# ActaTrace — Carga Segura de Actas y Tratamiento de Boletas

**Documento:** Proceso de carga, validación y seguridad documental  
**Versión:** 1.0 · Mayo 2026  
**Clasificación:** Público técnico

---

## 1. Principio rector

ActaTrace debe registrar y verificar **actas electorales digitalizadas**, no boletas individuales, salvo que exista una autorización legal, operativa y documental explícita.

Las actas son documentos de cierre y resultados. Las boletas individuales pueden revelar intención de voto y tienen un nivel de sensibilidad mayor. Por defecto, el MVP de ActaTrace no debe recibir, procesar, publicar ni registrar boletas individuales.

> Regla base: ActaTrace verifica la integridad documental del acta registrada, no sustituye el proceso legal de conteo ni custodia física.

---

## 2. Alcance documental

| Documento | Se permite en MVP | Tratamiento |
|---|---:|---|
| Acta de casilla digitalizada | Sí | Carga, hash, auditoría, verificación y registro blockchain |
| Acta PREP o captura equivalente | Sí | Comparación contra acta fuente y auditoría |
| Evidencia complementaria autorizada | Condicional | Solo con rol, motivo y clasificación |
| Boleta individual | No por defecto | Requiere autorización formal y flujo especial |
| Credenciales, listados nominales o datos personales masivos | No | Fuera de alcance del MVP |

Si una implementación futura requiere boletas individuales, debe diseñarse como módulo separado, con análisis legal, privacidad reforzada, controles de custodia y aprobación explícita.

---

## 3. Roles de carga y revisión

| Rol | Permisos recomendados |
|---|---|
| `CAPTURISTA` | Cargar actas asignadas a su zona operativa |
| `SUPERVISOR` | Validar, rechazar o marcar inconsistencias |
| `AUDITOR` | Consultar bitácora y evidencia sin alterar registros |
| `ADMIN_ELECTORAL` | Gestionar catálogos, usuarios, zonas y reglas |
| `OBSERVADOR` | Consulta de solo lectura cuando esté permitido |
| `CIUDADANO` | Consulta pública sin registro, sin acceso a documentos sensibles |

Los permisos deben aplicarse en backend. La interfaz no es una barrera de seguridad suficiente.

---

## 4. Flujo de carga de actas

1. El usuario autorizado inicia sesión.
2. El sistema valida rol, permisos territoriales y estado de operación.
3. El usuario selecciona archivo permitido: PDF, JPG o PNG.
4. El backend valida tipo real de archivo, tamaño, estructura y legibilidad básica.
5. El sistema solicita metadatos obligatorios:
   - elección
   - entidad
   - distrito
   - sección
   - casilla
   - tipo de acta
   - folio o identificador documental
   - origen del documento
6. El backend verifica que la casilla exista en catálogo.
7. El backend verifica que el usuario pueda cargar documentos para esa zona.
8. El archivo pasa por escaneo de malware.
9. El backend calcula el hash SHA-256 del archivo original.
10. El documento se guarda en storage privado.
11. PostgreSQL registra metadatos, hash, usuario, timestamp y estado inicial.
12. La bitácora de auditoría registra el evento `DOCUMENT_UPLOADED`.
13. El registro queda en estado `PENDING_REVIEW` o `PENDING_BLOCKCHAIN`, según el flujo aprobado.
14. Un worker encola el hash para registro blockchain si corresponde.

El archivo original debe permanecer inmutable. Cualquier corrección debe registrarse como nuevo evento, no como reemplazo silencioso.

---

## 5. Cercos de seguridad

### Autenticación

- Inicio de sesión obligatorio para carga.
- Contraseñas con hashing seguro o proveedor de identidad confiable.
- MFA recomendado para perfiles administrativos y supervisores.
- Sesiones con expiración y revocación.

### Autorización

- Control por rol.
- Control por entidad, distrito, sección o casilla asignada.
- Reglas de backend para impedir cargas fuera de jurisdicción.
- Separación entre usuario que carga y usuario que valida cuando sea posible.

### Validación de archivo

- Permitir solo formatos aprobados.
- Validar MIME real y firma del archivo, no solo extensión.
- Definir tamaño máximo.
- Rechazar archivos corruptos, vacíos o ilegibles.
- Escanear malware antes de disponibilidad interna.
- Normalizar metadatos técnicos sin alterar el archivo original.

### Integridad

- Calcular hash SHA-256 inmediatamente después de recibir el archivo.
- Guardar el hash junto con tamaño, tipo, timestamp y usuario.
- Detectar duplicados por hash.
- Detectar conflicto si existe otra acta activa para la misma casilla y tipo.
- Registrar cada cambio de estado en bitácora.

### Storage

- Guardar archivos originales en storage privado.
- Usar cifrado en reposo.
- Usar nombres internos no adivinables.
- Servir documentos privados mediante URLs firmadas temporales.
- Registrar cada lectura, descarga o previsualización sensible.

### Auditoría

- Registrar usuario, rol, IP, user agent, timestamp y acción.
- No permitir edición directa de eventos de auditoría.
- Registrar motivo obligatorio para rechazo, corrección o reemplazo.
- Mantener relación entre documento anterior y nueva versión cuando exista corrección.

### Protección pública

- El Portal Ciudadano debe mostrar solo información pública y verificable.
- No debe exponer datos personales, documentos sensibles o URLs permanentes.
- Debe mostrar claramente si un documento está pendiente, confirmado o en revisión.

---

## 6. Estados documentales recomendados

| Estado | Significado |
|---|---|
| `DRAFT` | Captura iniciada, aún no confirmada |
| `UPLOADED` | Archivo recibido y almacenado |
| `HASHED` | Hash generado correctamente |
| `PENDING_REVIEW` | Esperando revisión de supervisor |
| `APPROVED` | Acta validada internamente |
| `REJECTED` | Acta rechazada con motivo registrado |
| `CONFLICT_DETECTED` | Existe duplicidad o contradicción |
| `PENDING_BLOCKCHAIN` | Hash en cola de registro blockchain |
| `CONFIRMED_ON_CHAIN` | Hash confirmado en blockchain |
| `MISMATCH_DETECTED` | El archivo no coincide con el hash esperado |

El estado público nunca debe afirmar verificación completa si falta revisión o confirmación requerida.

---

## 7. Correcciones y reemplazos

Una acta no debe reemplazarse de forma silenciosa.

Si se requiere corrección:

1. El usuario autorizado solicita corrección con motivo.
2. El sistema conserva el archivo anterior.
3. Se carga el nuevo archivo como nueva versión o nuevo evento.
4. Se calcula nuevo hash.
5. Se relaciona con el documento previo.
6. Supervisor o auditor valida el cambio.
7. La bitácora registra quién, cuándo, por qué y qué cambió.
8. Blockchain registra el nuevo evento crítico si aplica.

Esto permite reconstruir la historia completa del documento.

---

## 8. Tratamiento de boletas individuales

Las boletas individuales quedan fuera del MVP.

Razones:

- Pueden revelar intención de voto.
- Tienen mayor riesgo de privacidad y manipulación.
- Su digitalización masiva puede crear nuevos vectores de exposición.
- Su validez depende de reglas legales y cadena de custodia física.

Si en el futuro se habilita carga de boletas, deben existir como mínimo:

- Dictamen legal específico.
- Consentimiento o fundamento normativo aplicable.
- Clasificación documental separada.
- Storage aislado.
- Cifrado reforzado.
- Acceso restringido por caso.
- Auditoría ampliada.
- Prohibición de publicación ciudadana directa.
- Política de retención y eliminación.

Sin esos elementos, el sistema debe rechazar boletas individuales.

---

## 9. Riesgos principales

| Riesgo | Control |
|---|---|
| Archivo malicioso | Validación y escaneo de malware |
| Suplantación de capturista | MFA, sesiones seguras y auditoría |
| Carga fuera de jurisdicción | Autorización territorial en backend |
| Reemplazo silencioso | Versionado, hash y bitácora inmutable |
| Exposición de datos sensibles | Storage privado y minimización pública |
| Duplicidad de actas | Detección por casilla, tipo y hash |
| Error humano de captura | Revisión, estados y trazabilidad |
| Confianza excesiva en blockchain | Comunicación clara de límites |

---

## 10. Criterios de aceptación

El proceso de carga se considera correcto si:

- Solo usuarios autorizados pueden cargar actas.
- El backend valida archivo, permisos y metadatos.
- Cada archivo original genera hash SHA-256.
- El archivo original queda almacenado de forma privada e inmutable.
- Cada acción relevante queda auditada.
- Duplicados y conflictos se detectan.
- Correcciones preservan historial completo.
- El Portal Ciudadano no expone datos sensibles.
- Las boletas individuales son rechazadas por defecto.
- Blockchain recibe solo hashes y eventos críticos, nunca documentos completos.

