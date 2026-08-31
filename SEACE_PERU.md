# SEACE Perú — viabilidad de descarga y análisis de licitaciones

*Análisis para replicar en Perú el motor de licitaciones que hoy opera sobre
Mercado Público (Chile). Documento de decisión, no de implementación.*

---

## Veredicto

**Sí se puede, y con mejor materia prima que Chile en la parte de datos
estructurados históricos; peor en la parte de tiempo real.**

La diferencia de fondo con Chile es que **Perú no tiene un equivalente directo a
`api.mercadopublico.cl`**: no existe (públicamente documentada) una API REST de
"licitaciones vigentes hoy" con token. Lo que hay es:

1. un **portal OCDS con API y descargas masivas diarias** (excelente para
   histórico, análisis y match; con latencia de un día),
2. un **portal de datos abiertos (CONOSCE)** con datasets desde 2018,
3. el **buscador público del SEACE**, que sí tiene el dato del día y los
   documentos, pero está detrás de captcha en su versión clásica,
4. la **nueva plataforma de la Ley 32069**, que es una SPA sobre servicios REST
   JSON y parece ser el camino limpio hacia adelante.

La combinación (2)+(3)/(4) cubre el 100 % del caso de uso: monitoreo continuo,
ingesta de bases y match por RAG. El costo de ingeniería está concentrado en el
scraping de tiempo real y en la descarga de documentos, exactamente igual que en
Chile (donde la API tampoco entrega los adjuntos).

> **Estado de verificación:** este análisis se construyó con fuentes públicas.
> **No pude probar los endpoints en vivo**: la política de egreso de esta sesión
> bloquea los dominios `*.gob.pe`, `contratacionesabiertas.*` y
> `data.open-contracting.org` (403 en el CONNECT del proxy). Antes de
> comprometer plazos, corran `scripts/probe_seace.py` desde una red con salida
> libre y confirmen los cuatro puntos marcados **[verificar]**.

---

## Las cuatro fuentes, en orden de conveniencia

### 1. Portal de Contrataciones Abiertas — OCDS (la base del histórico)

- `https://contratacionesabiertas.oece.gob.pe/` (antes `osce.gob.pe`)
- API con tres familias de endpoints: **release**, **record** y **files**
  (descargas masivas). Formatos CSV, XLSX, JSON y SHA.
- Cubre datos transformados desde **SEACE V1, V2 y V3**; prefijo OCID
  `ocds-dgv273`, con sufijo por sistema de origen (p. ej. `ocds-dgv273-seacev2`).
- **Descargas actualizadas a diario** (`/descargas`).
- Extensiones propias útiles: moneda y tipo de cambio, valor total del ítem,
  cierre de contrato con monto final, departamento.

**Para qué sirve:** cargar de una sola vez todo el histórico, entrenar el
matching, construir la vista de mercado (quién compra qué, a qué precios, con qué
proveedores), y mantener la base al día con un delta diario.

**Para qué no sirve:** avisar hoy de una convocatoria publicada hoy. Y OCDS
referencia documentos, pero no es su repositorio.

**[verificar]** forma exacta de los endpoints y si `files` permite delta por
fecha o sólo paquetes completos por año.

### 2. CONOSCE / Portal de Datos Abiertos del OECE

- `https://bi.seace.gob.pe/pentaho/...` (Pentaho BI, descargas Excel/CSV).
- Datasets: **PAC** (Plan Anual de Contrataciones), procedimientos convocados,
  procedimientos adjudicados, contratos, proveedores adjudicados, consorcios,
  entidades contratantes, órdenes de compra y de servicio, miembros de comités
  de selección, subasta inversa y contrataciones directas.
- Cobertura **desde 2018**, incluye regímenes distintos a la ley general que
  igualmente se registran en SEACE.

**El PAC es el activo diferencial frente a Chile.** Es la intención de compra
declarada por cada entidad *antes* de convocar: permite alertar al cliente meses
antes de que exista la licitación. Mercado Público no tiene un equivalente de esa
calidad.

### 3. Buscador Público del SEACE v3 (el dato del día y los documentos)

- `https://prod2.seace.gob.pe/seacebus-uiwd-pub/buscadorPublico/buscadorPublico.xhtml`
  (también servido históricamente desde `prodapp2`).
- No requiere login para consultar. Permite búsqueda avanzada por entidad,
  objeto, departamento, rango de fechas y montos; y desde la **ficha de
  selección** se descargan bases, anexos, absolución de consultas, integración de
  bases, actas y el listado de participantes.
- **Fricciones reales:** es JSF/PrimeFaces con estado de sesión (`ViewState`),
  paginación por POST y **captcha**. No es una API; es una aplicación pensada
  para humanos.
- Hay precedente público de que se puede automatizar: el scraper
  [`Ed1123/seace-scraper`](https://github.com/Ed1123/seace-scraper) (Scrapy +
  Selenium) recorre el buscador por rango de fechas y exporta CSV, resolviendo el
  captcha manualmente en terminal. Es prueba de concepto, no producción, pero
  confirma que la mecánica funciona.

### 4. Nueva plataforma bajo la Ley 32069 (a dónde va todo)

- `https://prod6.seace.gob.pe/buscador-publico` — buscador nuevo, arquitectura
  SPA.
- Detrás hay **servicios REST JSON**, no JSF. Hay URLs de descarga directa de
  archivos públicos indexadas por buscadores, del tipo
  `https://prod6.seace.gob.pe/v1/s8uit-services/archivo/archivos-publico/descargar-archivo-contrato/{id}`,
  que responden sin autenticación.
- Si el buscador nuevo expone su búsqueda por el mismo tipo de servicio, **el
  captcha deja de ser un problema** y la ingesta de tiempo real pasa de "scraping
  frágil" a "cliente HTTP contra JSON no documentado".

**[verificar]** — esto es lo más importante de todo el documento. Abrir
`prod6.seace.gob.pe/buscador-publico` con las DevTools en la pestaña Network,
hacer una búsqueda y capturar: URL del servicio de búsqueda, forma del request
(GET/POST, filtros, paginación), forma de la respuesta y si hay captcha o token.
Diez minutos de trabajo que definen la arquitectura completa de la fase 2.

---

## El marco legal cambió, y eso es el riesgo principal

- La **Ley 32069** (Ley General de Contrataciones Públicas) rige desde el
  **22 de abril de 2025**, con su reglamento de enero de 2025.
- Crea **PLADICOP**, la plataforma digital que centraliza SEACE, RNP, catálogo
  electrónico, cuaderno de obra digital y contrataciones menores.
- Mientras PLADICOP despliega módulos, **SEACE 3.0 sigue operando** y se
  convierte progresivamente en módulo de consulta y trazabilidad del nuevo
  ecosistema.

**Consecuencia práctica:** durante 2025–2026 conviven dos universos de datos —
procedimientos del régimen anterior en el SEACE clásico y procedimientos nuevos
en la plataforma nueva. Cualquier diseño que asuma una sola fuente se rompe.
El motor tiene que ser **multi-fuente desde el día uno**, con un normalizador que
entregue un único esquema aguas arriba. Que es, exactamente, lo que ya exige
tener Chile y Perú en el mismo producto.

---

## Perú vs. Chile, lado a lado

| | Mercado Público (Chile) | SEACE / OECE (Perú) |
|---|---|---|
| API REST oficial documentada | Sí, con ticket | No para tiempo real; sí API OCDS sobre histórico |
| Latencia del dato | Minutos | ~1 día por OCDS/CONOSCE; tiempo real sólo por el buscador |
| Histórico masivo | Limitado por la API, día a día | Descargas masivas desde 2018, CSV/XLSX/JSON |
| Estándar | Propio | **OCDS** (interoperable, ya modelado por terceros) |
| Plan de compras anticipado | Débil | **PAC**, fuerte — alerta anticipada |
| Bases y anexos | No vienen por API → scraping | No vienen por datos abiertos → scraping o servicio de archivos |
| Captcha | No | Sí en el buscador clásico; **[verificar]** en el nuevo |
| Clasificador de rubro | Rubros ONU (UNSPSC) | CUBSO, construido sobre UNSPSC |
| Estabilidad de la plataforma | Alta | En transición SEACE → PLADICOP |

El último punto del cuadro es una oportunidad: si CUBSO y los rubros ONU
comparten raíz UNSPSC, **el mismo perfil de capacidades de un cliente sirve para
buscar en los dos países** sin rehacer la taxonomía. **[verificar]** el mapeo
real de códigos antes de darlo por hecho.

---

## Qué habría que construir

El motor de licitaciones de DOOIF ya está planteado como monitoreo → ingesta de
bases → RAG → alertas. Perú no cambia el motor; cambia sólo el adaptador de
entrada.

```
  Adaptadores de fuente          Núcleo (país-agnóstico)
  ─────────────────────          ───────────────────────
  Chile  · API MP          ┐
  Perú   · OCDS bulk/API   ├──►  Normalizador → esquema único
  Perú   · CONOSCE (PAC)   │         │
  Perú   · Buscador SEACE  ┘         ├──► Cola de documentos → OCR → embeddings
                                     ├──► Match RAG contra capacidades del cliente
                                     └──► Alertas y apoyo a la oferta
```

**Esquema único mínimo:** id de fuente + código nativo (OCID en Perú), entidad
compradora (con RUC/RUT), objeto (bien / servicio / obra / consultoría), rubro
normalizado a UNSPSC, monto referencial + moneda, fechas (convocatoria, consultas,
presentación de ofertas, buena pro), estado, ítems, documentos, y adjudicación
(proveedor + monto) cuando exista.

### Fases y esfuerzo

| Fase | Qué entrega | Esfuerzo aprox. |
|---|---|---|
| 0 · Validación | Correr el probe, confirmar los cuatro **[verificar]** | 1 día |
| 1 · Histórico | Carga masiva OCDS + CONOSCE, normalizador, esquema único, primeras consultas de mercado | 1–2 semanas |
| 2 · Tiempo real | Ingesta diaria de convocatorias (servicios del buscador nuevo si existen; scraping con captcha si no) | 1–3 semanas, según el resultado de la fase 0 |
| 3 · Documentos | Descarga de bases y anexos, OCR, ingesta a la capa de conocimiento | 1 semana (reutiliza lo de Chile) |
| 4 · Producto | Match RAG, alertas, PAC como alerta anticipada | reutiliza el motor; sólo tuning |

El rango de la fase 2 es el riesgo real del proyecto y se cierra con un día de
trabajo en la fase 0.

---

## Riesgos, sin adornos

1. **Transición SEACE → PLADICOP.** Los endpoints pueden cambiar durante el
   proyecto. Mitigación: adaptadores aislados, contrato de datos estable hacia
   adentro, y monitoreo de esquema que avise cuando una fuente cambia de forma.
2. **Captcha en el buscador clásico.** Si el buscador nuevo no expone servicios
   abiertos, la ingesta de tiempo real exige navegador automatizado y resolución
   de captcha, con el costo operativo y la fragilidad que eso implica. La
   alternativa aceptable: vivir con la latencia de un día del OCDS para la
   mayoría de los rubros, y reservar el scraping para los clientes que pagan por
   el aviso inmediato.
3. **Calidad del dato OCDS.** Están documentados problemas de identificadores de
   organización duplicados, contratos sin estado y códigos no documentados en
   algunos campos. Hay que presupuestar limpieza y deduplicación por RUC.
4. **Términos de uso y carga.** Antes de operar en producción conviene revisar
   los términos del portal y fijar límites de tasa conservadores; scraping
   agresivo contra un portal estatal es un problema evitable.

---

## Recomendación

Empezar por el **histórico OCDS + CONOSCE**, que es dato abierto, masivo, limpio
de fricciones legales y suficiente para demostrarle valor a un cliente peruano en
dos semanas (mapa de su mercado, quién le gana, a qué precios). En paralelo,
gastar un día en las DevTools del buscador nuevo: si expone JSON, Perú termina
siendo **más fácil de integrar que Chile**; si no, se entra con la latencia de un
día y el scraping queda como upgrade vendible aparte.

---

## Fuentes

- [Portal de Contrataciones Abiertas de la Compra Pública (OCDS) — OECE](https://contratacionesabiertas.oece.gob.pe/)
- [Acceder al Portal de Contrataciones Abiertas — gob.pe](https://www.gob.pe/52005-acceder-al-portal-de-contrataciones-abiertas-de-la-compra-publica-ocds)
- [OSCE implementa el Estándar OCDS — gob.pe](https://www.gob.pe/institucion/oece/noticias/884163-osce-implementa-el-estandar-de-datos-para-las-contrataciones-abiertas-ocds)
- [Acceder al Portal de Datos Abiertos del OECE — gob.pe](https://www.gob.pe/14272-acceder-al-portal-de-datos-abiertos-del-oece)
- [CONOSCE — Datos Abiertos](https://bi.seace.gob.pe/pentaho/api/repos/:public:portal:datosabiertos.html/content?userid=public&password=key)
- [Perú (OECE) en el OCP Data Registry](https://data.open-contracting.org/en/publication/135)
- [SEACE 3.0 — Buscador Público](https://prod2.seace.gob.pe/seacebus-uiwd-pub/buscadorPublico/buscadorPublico.xhtml)
- [Manual del Buscador Público SEACE v3.0 (PDF oficial)](https://cdn.www.gob.pe/uploads/document/file/4909242/Manual%20de%20Usuario%20Buscador%20publico%20Seace%20v2.5%20-%20VIGENTE.pdf)
- [Ed1123/seace-scraper — scraper de referencia](https://github.com/Ed1123/seace-scraper)
- [Ley 32069, Ley General de Contrataciones Públicas (actualizada)](https://lpderecho.pe/ley-general-de-contrataciones-publicas-actualizada/)
- [¿Qué es el PLADICOP? — LP Derecho](https://lpderecho.pe/contrataciones-estado-pladicop/)
- [SEACE y PLADICOP bajo la Ley 32069 — CEPEG](https://cepeg.pe/blog/curso-seace-pladicop-ley-32069/)
