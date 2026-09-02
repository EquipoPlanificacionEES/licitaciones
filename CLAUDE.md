# CLAUDE.md — contexto permanente del proyecto

Este archivo lo lee Claude Code automaticamente al abrir una sesion en esta
carpeta (PowerShell, terminal o claude.ai/code). Sirve para no tener que
volver a explicar el proyecto en cada sesion.

## Que es esto

Repositorio `licitaciones` de **DOOIF**. DOOIF es una plataforma unica
(**DOOIF Core**) sobre la que se construyen todos los productos como "caras"
del mismo nucleo. La tesis: *DOOIF no vende IA, vende conocimiento*.

El documento fundacional completo — filosofia, principios innegociables,
arquitectura del Core, soluciones, modelo comercial, roadmap y pitch — esta en
**`DOOIF.md`**. Leelo antes de proponer cambios de contenido o de estrategia.

Este repo cumple hoy dos funciones:

1. **Material comercial de DOOIF** (lo que existe): la web, el libro PDF y el
   libro interactivo.
2. **Motor de Licitaciones** (por construir): inteligencia de compra publica —
   monitoreo de portales, ingesta de bases y anexos a la capa de conocimiento,
   match RAG entre requisitos y capacidades del cliente, alertas y apoyo a la
   preparacion de ofertas.

## Estructura

| Ruta | Que es |
|---|---|
| `DOOIF.md` | Documento fundacional v1.0. Fuente de verdad del discurso. |
| `web/index.html` | Web comercial dooif.cl. Pagina unica, autocontenida (sin build). |
| `libro/libro.template.html` | Fuente del libro para clientes. Placeholders `@@FONT@@`, `@@CUBE@@`, `@@CUBE2@@`. |
| `libro/build_libro.py` | Genera `libro.html` desde la plantilla (inyecta fuente base64 y los cubos SVG). El PDF se imprime desde ese HTML. |
| `libro/DOOIF_Libro.pdf` | Libro edicion clientes, 16 paginas. Artefacto generado. |
| `libro/archivo-latin.b64` | Fuente tipografica embebida en base64. |
| `interactivo/interactivo.template.html` | Fuente del libro interactivo. Placeholders `@@FONT@@`, `@@CUBOSVG@@`, `@@CUBOSVG2@@`. |
| `interactivo/DOOIF_Interactivo.html` | Libro interactivo enviable por correo, un solo archivo. Artefacto generado. |

## Reglas de trabajo

- **Editar la plantilla, no el generado.** Los cambios de `libro/` e
  `interactivo/` van en el `*.template.html`; despues se regenera el artefacto.
  Editar solo el HTML final se pierde en la siguiente regeneracion.
- **Un solo archivo, sin dependencias externas.** La web, el libro y el
  interactivo deben abrir con doble clic y funcionar sin servidor, sin CDN y
  sin conexion: CSS y JS inline, fuentes e imagenes embebidas.
- **El contenido degrada sin JavaScript.** En el interactivo todo el texto debe
  verse aunque el JS no corra; los efectos se activan con una clase `js`.
- **Movil primero en lo enviable.** Se prueba en viewport de 390px ademas de
  escritorio.
- **El discurso sale de `DOOIF.md`.** Nada de inventar productos, cifras,
  clientes ni fechas que no esten ahi. Si falta un dato, se pregunta.
- **Mensajes de commit sin tildes ni caracteres especiales**, en espanol,
  describiendo el resultado (ver `git log`).

## Falta por hacer

- No hay script de build para `interactivo/` (equivalente a `build_libro.py`).
  Hoy la generacion es manual.
- El motor de licitaciones no esta implementado: el repo aun no tiene codigo de
  aplicacion, solo material comercial.
