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

## Adjudicaciones del día, ganadores y documentación de la oferta

Tres preguntas distintas, con tres respuestas distintas: la primera es fácil, la
segunda es el punto más fuerte del SEACE, y la tercera es la única que tiene un
"depende" real.

### a) El Excel de procedimientos vigentes, automatizado

El buscador público exporta a Excel los resultados de la búsqueda; es la
descarga manual que ya conocen. Automatizarla tiene tres caminos, en orden de
preferencia:

1. **No automatizarla.** El dataset CONOSCE de *procedimientos convocados* y el
   *release* OCDS entregan lo mismo en CSV/JSON estructurado, sin captcha y sin
   navegador. Cuesta un día de trabajo y no se rompe. La contra es la latencia
   de ~1 día.
2. **Servicios del buscador nuevo** (`prod6`), si expone JSON — pendiente de
   verificar, pero es el camino limpio para el mismo día.
3. **Replicar el POST del buscador clásico**, que exige mantener el `ViewState`
   de JSF y resolver el captcha. Es el último recurso.

Nota importante: el Excel del buscador es **la lista, no las bases**. Trae la
cabecera del procedimiento (entidad, objeto, nomenclatura, fechas, valor
referencial, estado); los documentos siguen estando uno a uno en cada ficha.

### b) Identificar las adjudicadas del día y quién ganó — sí, y bien

Esto está resuelto por norma, no por suerte: **el otorgamiento de la buena pro se
publica en el SEACE el mismo día de su realización**, y la publicación debe ir
acompañada del **acta de otorgamiento de la buena pro** y del **cuadro
comparativo**, con los documentos que sustentan los resultados de calificación y
evaluación de los postores.

Fuentes para capturarlo, según la latencia que se necesite:

| Vía | Latencia | Qué entrega |
|---|---|---|
| Buscador público, filtrando por fecha y estado | Mismo día | Ficha, acta, cuadro comparativo |
| **Buscador de Proveedores Adjudicados** | Mismo día / muy baja | Adjudicaciones por RUC o DNI **desde 2008**, individuales y en consorcio, incluidas órdenes de compra y servicio hasta 8 UIT. Exporta Excel |
| CONOSCE: *procedimientos adjudicados* y *proveedores adjudicados* | ~1 día | Dataset completo, ideal para carga masiva |
| OCDS: bloque `awards` con `suppliers` | ~1 día | Adjudicación normalizada, lista para el esquema único |

**El cuadro comparativo es el activo que Chile no da con esta facilidad.** No
dice sólo quién ganó: dice **cuánto ofertó cada postor** y qué puntaje obtuvo.
Con eso, sobre el histórico, se construye algo que vale por sí solo como
producto:

- a qué porcentaje del valor referencial gana cada competidor, por rubro y por
  entidad;
- quién compite realmente contra el cliente y en qué tipos de procedimiento;
- qué entidades tienen un único postor recurrente;
- cuál es el precio de corte esperable para un procedimiento nuevo.

Eso es **inteligencia de precios para preparar la oferta**, no sólo alertas. Es
la funcionalidad que justifica el proyecto peruano por encima de "avisar de
licitaciones".

### c) Extraer la documentación de la oferta del ganador — con matices

Hay que separar tres capas, porque tienen garantías legales distintas:

| Capa | ¿Público? | Comentario |
|---|---|---|
| Acta de buena pro y cuadro comparativo | **Sí, por norma, el mismo día** | Montos y puntajes por postor |
| Documentos que sustentan calificación y evaluación | **Sí, por norma** | Acompañan la publicación de la buena pro |
| Oferta completa del ganador (propuesta técnica con anexos, certificados, detalle económico) | **Depende** | Existe en digital — en los procedimientos electrónicos la oferta se presenta por la plataforma — pero su publicación al público hay que confirmarla ficha por ficha |
| Ofertas de los perdedores | Normalmente no | Salvo lo que aparezca en el cuadro comparativo |

Dos límites que hay que asumir de entrada: la **información confidencial**
(secreto comercial o tecnológico que el postor justifique) y los **datos
personales** no se publican, así que ninguna oferta va a estar íntegra y sin
tachas.

Y una vía adicional que conviene probar antes que cualquier otra cosa: **el
contrato suscrito sí se registra en el SEACE** y tiene su propio buscador
(`prod4.seace.gob.pe/contratos/publico/`, con endpoints de descarga directa de
archivo del tipo `.../descargar-archivo-contrato/{id}` en la plataforma nueva,
que responden sin autenticación). Los contratos suelen incorporar la oferta
ganadora como anexo. **[verificar]** si en la práctica esos anexos vienen
adjuntos: si la respuesta es sí, el problema de la capa 3 queda resuelto por una
puerta lateral, y además abierta y sin captcha.

Si aun así falta la oferta de un procedimiento concreto y de verdad se necesita,
queda el canal formal: **solicitud de acceso a la información pública** a la
Entidad (Ley 27806). El expediente de contratación es público salvo lo
confidencial, y hay plazo legal de respuesta. Sirve para casos puntuales de alto
valor; no es automatizable a escala y no debe estar en el camino crítico del
producto.

### Verificación empírica pendiente (15 minutos, alto valor)

Abrir 4 o 5 fichas de procedimientos **con buena pro reciente**, de tipos
distintos (licitación pública, concurso público, adjudicación simplificada,
subasta inversa electrónica), y anotar para cada una:

1. qué tipos de documento aparecen listados y descargables;
2. si está el cuadro comparativo con montos por postor;
3. si aparece la oferta del ganador y en qué formato;
4. si el contrato publicado trae la oferta como anexo;
5. si la descarga de cada documento tiene URL directa estable (con id) o exige
   sesión y captcha.

Con esa tabla en la mano, el alcance de la fase 3 deja de ser una estimación y
pasa a ser un hecho.

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

Y un ajuste de foco respecto del planteamiento original: en Perú el producto no
debería venderse sólo como *alerta de licitaciones*. Con el cuadro comparativo y
las adjudicaciones desde 2008, lo vendible es **con cuánto hay que entrar para
ganar**, quién compite y a qué descuento gana. La alerta es la puerta de entrada;
la inteligencia de precios es lo que se paga.

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
- [Consultar los buscadores públicos del SEACE — gob.pe](https://www.gob.pe/7505-consultar-los-buscadores-publicos-del-sistema-electronico-de-contrataciones-del-estado-seace)
- [Acceder al Buscador de Proveedores Adjudicados — gob.pe](https://www.gob.pe/14273-acceder-al-buscador-de-proveedores-adjudicados)
- [Buscador de Proveedores del Estado](https://apps.osce.gob.pe/perfilprov-ui/buscar)
- [SEACE — Buscador de Contratos](https://prod4.seace.gob.pe/contratos/publico/)
- [Directiva N.° 007-2025-OECE-CD, registro de información en el SEACE](https://www.gob.pe/institucion/oece/normas-legales/6682412-007-2025-oece-cd)
- [Reglamento de la Ley 32069 (DS 009-2025-EF), por artículos](https://simuladoroece.org/reglamento-ley-32069/)
- [Otorgamiento de la buena pro bajo la Ley 32069 — Perucontrata](https://www.perucontrata.com.pe/ley-reglamento-contrataciones/otorgamiento-buena-pro/)
