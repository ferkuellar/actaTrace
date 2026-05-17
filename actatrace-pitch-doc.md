# ActaTrace — Pitch Deck · Guía de Diapositivas para PPT

**Audiencia:** Inversionistas GovTech · Aceleradoras institucionales  
**Duración:** 3–4 minutos  
**Slides totales:** 7

---

## SLIDE 1 — PORTADA

**Título principal:**  
# ActaTrace

**Subtítulo:**  
La capa de verificación que hace los resultados electorales auditables por cualquier ciudadano, sin depender de la confianza en ninguna institución.

**Elementos visuales:**
- Logotipo: símbolo de rombo/trazado con punto central (representa trazabilidad)
- Fondo oscuro (#09090b) con malla de cuadrícula sutil y gradiente azul profundo
- Tags: `GovTech` · `Blockchain` · `Trazabilidad Electoral` · `MVP 2026`

**Notas de diseño:**
- Tipografía: IBM Plex Sans Bold para el título, light para el subtítulo
- Sin imágenes de stock. Sin fotos de votos ni urnas.
- Color de acento: `#0C5CAB` para "Trace"

---

## SLIDE 2 — EL PROBLEMA

**Título:** Los ciudadanos no pueden verificar los resultados.

**Tres problemas centrales:**

**1. El PREP no tiene evidencia vinculada**  
Los resultados preliminares no están conectados con el acta física que los respalda. Se declaró. No se demostró.

**2. La cadena de custodia es opaca**  
No existe registro público de quién manipuló cada documento, cuándo ni en qué condición llegó.

**3. La detección de inconsistencias depende de humanos**  
Diferencias entre acta y PREP solo se detectan si alguien las busca manualmente.

**Estadísticas (columna derecha):**

| Stat | Detalle |
|---|---|
| **63%** | de mexicanos desconfía de los resultados electorales (Latinobarómetro 2023) |
| **+170K** | casillas electorales en elecciones federales — sin mecanismo de verificación ciudadana |
| **0** | sistemas públicos de verificación de integridad documental electoral en México |

**Notas de diseño:**
- Los números estadísticos en rojo (#ef4444) en cajas independientes
- Los 3 problemas con número de secuencia en círculo rojo
- Layout: 60% texto / 40% estadísticas

---

## SLIDE 3 — LA SOLUCIÓN

**Título:** Trazabilidad verificable, de principio a fin.

**Concepto central (destacado):**  
Cada acta genera un hash inmutable. Cada hash va a blockchain. Cualquier ciudadano puede verificar.

**Flujo de datos (lista visual):**

```
01 → Acta física → Upload
02 → Hash SHA-256 automático (huella digital única)
03 → PostgreSQL → Registro + metadatos
04 → Blockchain → Inmutabilidad verificable
05 → Portal Ciudadano → Verificación pública
```

**4 Módulos del MVP:**

| Módulo | Qué hace |
|---|---|
| 📄 Registro de Actas | Upload + SHA-256 + trazabilidad completa |
| ⛓ PREP Verificable | Acta fuente + comparación automática |
| 🔗 Cadena de Custodia | Quién, cuándo, en qué estado |
| 🌐 Portal Ciudadano | Verificación pública sin registro ni cuenta |

**Notas de diseño:**
- Flujo en caja oscura con fuente monospaced
- Módulos en tarjetas compactas (2x2 grid)
- Color verde (#10b981) para el hash / verificación

---

## SLIDE 4 — DEMO / PROTOTIPO

**Título:** Así lo usa un ciudadano.

**Texto de soporte:**  
Busca su casilla. Ve el resultado. Verifica el hash. Sin crear cuenta, sin depender de ninguna institución.

**4 puntos de la demo:**

- ✓ **Búsqueda por casilla o sección.** Resultado, votos y estado de verificación en segundos.
- ⛓ **Hash verificable en blockchain.** El ciudadano puede confirmar en la red pública, sin confiar en ActaTrace.
- ⚠ **Inconsistencias visibles.** Si el PREP difiere del acta, el sistema lo marca automáticamente con evidencia.
- 🔗 **Cadena de custodia pública.** Quién tocó el documento, cuándo y con qué rol.

**Mockup de pantalla (insertar captura del prototipo):**

```
Portal Ciudadano
────────────────────────────────────
🔍  Casilla 1042-B
────────────────────────────────────
✓ VERIFICADO

Casilla:    1042-B · Chihuahua
Votos acta: 342
Votos PREP: 342 ✓

SHA-256: a3f9c2d1e8b47f203c91a5d6...
TX: 0x8f2a3b91c44d6e7f...

⚠ Casilla 1087-A: Inconsistencia detectada
   PREP 291 ≠ Acta 289
```

**Notas de diseño:**
- Pantalla del prototipo como imagen o mockup a la derecha
- Puntos de feature a la izquierda
- Layout: 40% texto / 60% screenshot

---

## SLIDE 5 — IMPACTO DEMOCRÁTICO

**Título:** El problema es global. La oportunidad también.

**3 métricas de impacto:**

| Métrica | Descripción |
|---|---|
| **170K+ casillas** | Cada una puede ser registrada, hasheada y verificada públicamente |
| **100% auditables** | Sin acceso privilegiado. Cualquier ciudadano, observador o medio puede verificar. |
| **< 2 segundos** | Tiempo de verificación de integridad por casilla desde el portal público |

**Mercado (fila de estadísticas):**

| Dato | Valor |
|---|---|
| Países LATAM con elecciones anuales | 18 |
| Mercado global GovTech integridad electoral 2025 | $2.4B USD |
| Soluciones de trazabilidad de actas con blockchain en LATAM | **0** |
| Elecciones estatales en México 2026 | Ventana de piloto |

**Notas de diseño:**
- Las 3 métricas principales en tarjetas con número grande
- La fila de mercado en barra horizontal al pie del slide
- "0 soluciones en LATAM" en color de acento como oportunidad

---

## SLIDE 6 — VIABILIDAD TÉCNICA

**Título:** Stack maduro. Arquitectura auditable.

**Stack técnico (dos columnas):**

**Columna izquierda:**
- **Backend:** FastAPI (Python) · REST async
- **Base de datos:** PostgreSQL · fuente principal de datos
- **Cache:** Redis · colas de eventos
- **Auth:** JWT + RBAC · 6 roles
- **Frontend:** Next.js / React · Portal público y dashboard

**Columna derecha:**
- **Blockchain:** Hyperledger Fabric (permisionado) · solo hashes y eventos
- **Storage:** S3 / IPFS · documentos originales
- **Hash:** SHA-256 · estándar NIST
- **Infra:** Docker + Kubernetes + Terraform
- **Cloud:** AWS / OCI · CI/CD automatizado

**5 principios de arquitectura (chips):**
- 🔍 Auditabilidad primero
- 🧱 Capas desacopladas
- ⛓ Blockchain mínimo (no es la DB)
- 🌐 Open Source ready
- ⚖ LGIPE + LFPDPPP compliance

**Notas de diseño:**
- Dos columnas simétricas con cajas oscuras
- Chips de principios al pie como fila de badges
- Sin diagramas de arquitectura completos (ese es un documento separado)

---

## SLIDE 7 — LA PROPUESTA / CIERRE

**Título:** La evidencia que la democracia merece.

**Párrafo de cierre:**  
ActaTrace no pide que confíen en el sistema. Pide que lo verifiquen. Eso es exactamente el punto.

**Hoja de ruta (columna izquierda):**

| Trimestre | Hito |
|---|---|
| **Q3 2026** | Piloto con autoridad electoral estatal · 500 casillas · validación institucional |
| **Q4 2026** | MVP completo + Portal Ciudadano live · API pública documentada |
| **2027** | Expansión LATAM · Colombia, Perú, Chile |

**Propuesta financiera (columna derecha):**

**Inversión Seed:** $450K USD  
_18 meses · Equipo núcleo + infraestructura + piloto institucional_

**Modelo de ingresos:** B2G SaaS  
_Licencia anual por proceso electoral: $80K–$400K USD según escala_  
_Servicios de integración y auditoría técnica_

**Ventaja competitiva:**
- Primero en LATAM
- Sin datos personales en blockchain
- Auditabilidad sin depender de blockchain

**Quote de cierre:**  
> "Confianza no se declara. Se construye con evidencia verificable."

**Contacto:**  
contacto@actatrace.mx · actatrace.mx

---

## Notas de diseño global para PPT

**Paleta de colores:**
- Fondo: `#09090b` (negro profundo)
- Superficie de tarjetas: `#18181b`
- Bordes: `#27272a`
- Texto principal: `#fafafa`
- Texto secundario: `#a1a1aa`
- Azul primario: `#0C5CAB`
- Verde éxito: `#10b981`
- Ámbar advertencia: `#f59e0b`
- Rojo alerta: `#ef4444`
- Púrpura blockchain: `#a855f7`

**Tipografía:**
- Títulos: IBM Plex Sans Bold 800
- Cuerpo: IBM Plex Sans 400/600
- Código / hashes: IBM Plex Mono
- Alternativa si IBM Plex no está disponible: Manrope Bold + Inter

**Reglas generales:**
- Nunca usar fotos de stock de políticos, urnas o banderas
- Ilustraciones minimalistas o capturas del sistema
- Sin gradientes de arcoíris ni colores saturados
- Densidad media: ni slides vacías ni saturadas de texto
- Cada slide tiene una sola idea central

---

*ActaTrace · Pitch Deck v1.0 · Mayo 2026*
