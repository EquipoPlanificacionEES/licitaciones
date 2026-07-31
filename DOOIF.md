# DOOIF — Documento Maestro de Plataforma

> **DOOIF no vende IA. DOOIF vende conocimiento.**

Este es el documento fundacional de DOOIF: qué es, por qué existe, cómo está
construida, qué vende y hacia dónde va. Todo producto, proyecto, propuesta y
línea de código de la empresa debe ser coherente con lo que dice este documento.

---

## 0. Principios innegociables

Estos principios no se negocian. Ante cualquier decisión —técnica, comercial o
de producto— se vuelve a esta lista:

1. **DOOIF no vende IA. DOOIF vende conocimiento.** La IA es el medio; el
   producto es el conocimiento operativo que resuelve el problema del cliente:
   la llamada contestada, la cotización enviada, la licitación detectada, la
   gestión cerrada.
2. **La plataforma principal es DOOIF Core.** Existe una sola plataforma.
3. **Todos los productos usan el mismo Core.** Ningún producto se construye
   fuera del Core. Un producto es una cara del Core, no un sistema aparte.
4. **Los proyectos financian el producto.** Cada proyecto pagado por un cliente
   deja capacidades permanentes en la plataforma. El cliente paga su solución;
   DOOIF capitaliza el motor.
5. **Cada cliente agrega capacidades a la plataforma.** El Core es acumulativo:
   con cada cliente la plataforma sabe hacer más cosas que antes.
6. **Nunca desarrollar dos veces lo mismo. Siempre reutilizar.** Si un motor ya
   existe, se conecta. Si no existe, se construye una vez, dentro del Core, y
   queda disponible para todos los productos.
7. **La empresa es cloud-native. AWS.** Sin servidores propios, sin instalación
   en cliente. Todo servicio nace pensado para operar y escalar en la nube.
8. **Arquitectura desacoplada. APIs.** Los productos hablan con el Core por
   API. Los motores hablan entre sí por API. Cualquier pieza se puede
   reemplazar sin tocar el resto.
9. **Base vectorial. Embeddings. RAG. Motores especializados.** El conocimiento
   vive vectorizado y recuperable; los motores especializados lo transforman en
   acción.

---

## 1. Historia

DOOIF nace dentro de **Planificación EES Ingeniería** (Chile), una empresa de
ingeniería acostumbrada a resolver proyectos reales para clientes reales.

El patrón se repitió proyecto tras proyecto: cada solución a medida contenía
piezas que se volvían a necesitar en el proyecto siguiente — atender llamadas,
prospectar, cotizar, hacer seguimiento, agendar, cobrar, leer documentos y
responder sobre ellos. Reconstruir esas piezas cada vez era pagar dos veces por
lo mismo.

La respuesta fue dejar de tratar cada proyecto como un fin y empezar a tratarlo
como un ladrillo: **todo lo que se construye para un cliente queda como
capacidad permanente de una plataforma común**. Esa plataforma es **DOOIF
Core**, y la práctica ya está probada: el ecosistema Sinergia (agentes de voz
IVR entrante y saliente, chat web, prospección, cotizaciones con link público,
seguimiento multicanal, agenda de técnicos, cobros con pasarela, operación
SaaS multi-tenant con white-label) se construyó exactamente así, motor por
motor, financiado por el trabajo real que cada módulo salía a resolver.

DOOIF es el paso siguiente: darle nombre, arquitectura y modelo comercial a lo
que ya estaba ocurriendo.

*(Fechas, hitos y nombres propios de esta sección: completar/ajustar por el
equipo — este borrador narra el origen sin inventar datos duros.)*

## 2. Filosofía

- **Conocimiento antes que tecnología.** El cliente no compra un modelo de
  lenguaje ni una base vectorial; compra que su negocio sepa hacer algo que
  antes no sabía, o lo haga sin depender de una persona disponible. La
  tecnología es invisible cuando funciona.
- **Acumular, no repetir.** El activo de DOOIF es la suma de capacidades del
  Core. Cada línea de código duplicada destruye valor; cada motor reutilizado
  lo multiplica.
- **El proyecto es el laboratorio.** No se construye producto en el vacío: se
  construye resolviendo un problema pagado, con un cliente exigiendo que
  funcione. Lo que sobrevive al cliente real entra al Core.
- **Especialización sobre generalidad.** Un motor que hace una cosa muy bien
  (llamar, prospectar, cotizar, leer licitaciones) vale más que un asistente
  genérico que hace todo a medias. DOOIF compone motores especializados.
- **Desacoplado o no existe.** Todo con API, todo reemplazable: el proveedor de
  voz, el modelo de IA, la pasarela de pago, el canal de búsqueda. Ninguna
  dependencia es estructural.

## 3. Misión

Convertir el conocimiento de las empresas —sus documentos, sus procesos, su
experiencia— en capacidad operativa que trabaja sola: agentes y motores que
atienden, venden, cotizan, gestionan y detectan oportunidades las 24 horas,
sobre una única plataforma que crece con cada cliente.

## 4. Visión

Ser la plataforma de conocimiento operativo de referencia para las empresas de
habla hispana: que cualquier pyme o institución pueda enchufar su negocio a
DOOIF Core y obtener, en días y no en meses, las capacidades que hoy solo
tienen las grandes corporaciones. Una sola plataforma, muchos productos, cero
desarrollos repetidos.

## 5. Arquitectura

DOOIF Core es una plataforma **cloud-native sobre AWS**, **desacoplada** y
**orientada a APIs**, organizada en tres capas más los productos que la
consumen:

```
  PRODUCTOS        Sinergia   │  Agente Contactos  │  Licitaciones  │  (próximos…)
  (caras del Core)     └──────────────┬──────────────────┘
                                      │  APIs (REST / webhooks / WS)
                     ┌────────────────▼────────────────────────────────────┐
                     │                    DOOIF  CORE                      │
                     │                                                     │
                     │  MOTORES ESPECIALIZADOS                             │
                     │   voz (STT→cerebro→TTS) · prospección · seguimiento │
                     │   cotizaciones · agenda · cobros/pasarela · canales │
                     │   análisis documental · generación de agentes       │
                     │  ─────────────────────────────────────────────────  │
                     │  CAPA DE CONOCIMIENTO                               │
                     │   ingesta de fuentes → embeddings → base vectorial  │
                     │   → RAG (recuperación + generación con contexto)    │
                     │  ─────────────────────────────────────────────────  │
                     │  CAPA DE PLATAFORMA (SaaS)                          │
                     │   multi-tenant · auth/RBAC · planes y límites       │
                     │   white-label · superadmin · métricas y costos      │
                     └────────────────────────┬────────────────────────────┘
                                              │
                                    AWS (cloud-native)
```

**Capa de conocimiento.** El corazón del "vendemos conocimiento": las fuentes
del cliente (documentos, catálogos, bases de licitaciones, historiales) se
ingestan, se convierten en **embeddings** y se indexan en una **base
vectorial**. Los motores consultan ese conocimiento vía **RAG**: recuperan lo
relevante y generan respuestas y acciones con contexto real del cliente, no
con conocimiento genérico del modelo.

**Motores especializados.** Cada motor hace una cosa y la expone por API.
Varios ya existen y están en producción dentro del ecosistema Sinergia: motor
de voz (Deepgram STT → cerebro Claude → Azure TTS, canales GSM/Twilio y
WhatsApp Calling), prospección con búsqueda web conectable, seguimiento
multicanal, cotizaciones con link público, agenda con asignación de técnicos,
cobros con pasarela enchufable, chat web embebible, generador de agentes con
IA. Los próximos (p. ej. análisis de licitaciones) se suman al mismo catálogo.

**Capa de plataforma.** Lo que convierte los motores en un SaaS operable:
organizaciones multi-tenant con aislamiento por empresa, autenticación y RBAC,
planes de suscripción con límites de uso y trial, códigos de activación,
white-label por empresa y panel de superadministración.

**Reglas de arquitectura.**
- Todo proveedor externo (STT, TTS, LLM, pasarela, búsqueda) entra por una
  interfaz conectable: se puede cambiar de proveedor sin tocar los motores.
- Los productos no comparten código entre sí; comparten el Core.
- Ningún motor conoce la interfaz de usuario; solo expone API.
- Todo evento relevante (llamada, cotización, pago, hallazgo) se reporta por
  webhook al sistema de origen, con su contexto de vuelta.

## 6. Productos

Todos los productos son caras del mismo Core. Ninguno tiene motores propios.

### Sinergia (en producción)
Plataforma SaaS multi-tenant de ventas y atención para pymes. Incluye agentes
de voz IVR (entrantes y salientes por telefonía GSM, con WhatsApp Calling en
fase 2), chat web embebible, prospección automática con outreach, cotizaciones
con link público branded (aceptar/rechazar), motor de seguimiento multicanal
("no lo suelta"), agenda de trabajos con asignación de técnicos, cobros con
link propio y pasarela enchufable, y operación white-label por empresa.

### Agente Contactos
Gestión de contactos y gestiones: el agente llama, confirma datos, cierra o
actualiza gestiones, y devuelve resultado estructurado (transcripción +
análisis) al sistema de origen. Consume el motor de voz y el de seguimiento
del Core.

### Licitaciones (en construcción — este repositorio)
Inteligencia de licitaciones públicas: monitoreo continuo de portales de
compra pública, ingesta de bases y anexos a la capa de conocimiento, match por
RAG entre los requisitos de cada licitación y las capacidades reales de la
empresa cliente, alertas de oportunidades relevantes y apoyo a la preparación
de ofertas. Es el primer producto que nace ya declarado como cara del Core:
reutiliza ingesta, embeddings, base vectorial, RAG, seguimiento y
notificaciones; solo agrega el motor especializado de análisis de licitaciones,
que a su vez queda disponible para todos los demás productos.

### Próximos
Cada proyecto de cliente que requiera una capacidad nueva define el siguiente
producto potencial. La regla para abrir un producto: el motor ya fue pagado
por un proyecto y al menos dos clientes distintos lo necesitan.

## 7. Modelo Comercial

El modelo tiene tres motores de ingreso que se alimentan entre sí:

1. **Proyectos (financian el producto).** Soluciones a medida para clientes que
   pagan por resolver su problema concreto. Margen del proyecto + capacidad
   nueva que queda en el Core. Regla: no se acepta un proyecto cuyo desarrollo
   no deje al menos un motor o mejora reutilizable.
2. **Suscripción SaaS (recurrencia).** Productos sobre el Core vendidos por
   planes con límites de uso, trial y códigos de activación. La
   infraestructura ya existe (planes, límites, bloqueo por vigencia,
   multi-tenant, white-label).
3. **White-label y partners (escala).** Terceros (agencias, integradores)
   revenden los productos con su propia marca sobre la misma plataforma. DOOIF
   opera el Core; el partner pone la relación comercial.

**El círculo virtuoso:** un proyecto financia un motor → el motor se empaqueta
en un producto SaaS → el producto genera recurrencia y casos → los casos traen
más proyectos. Cada vuelta del círculo agranda el Core y baja el costo marginal
del siguiente cliente.

**Qué se cobra:** resultados y capacidad operativa (llamadas atendidas,
oportunidades detectadas, cotizaciones gestionadas), nunca "horas de IA" ni
licencias de tecnología. El precio se ancla al valor del conocimiento puesto a
trabajar.

## 8. Roadmap

*(Horizontes, no fechas; las fechas las fija el equipo por trimestre.)*

**Horizonte 1 — Consolidar el Core (ahora).**
- Extraer formalmente los motores de Sinergia como servicios del Core con API
  documentada (voz, prospección, seguimiento, cotizaciones, agenda, cobros).
- Levantar la capa de conocimiento como servicio transversal: ingesta →
  embeddings → base vectorial → RAG disponible para cualquier motor.
- Completar la operación cloud en AWS (hoy hay despliegues en Render;
  migrar/estandarizar según el principio AWS).
- Numeración 600/809 (norma SUBTEL) para llamadas comerciales en producción
  en Chile; WhatsApp Calling fase 2.

**Horizonte 2 — Licitaciones y segundo producto.**
- Construir el motor de licitaciones sobre la capa de conocimiento (este
  repositorio): monitoreo, ingesta de bases, match RAG, alertas.
- Primer cliente-proyecto de licitaciones financiando el desarrollo.
- Empaquetar Agente Contactos como producto SaaS independiente sobre el Core.

**Horizonte 3 — Plataforma abierta.**
- API pública del Core para partners e integradores.
- Marketplace de agentes y motores; catálogo de capacidades.
- White-label a escala: partners operando verticales propios (salud, inmobiliaria,
  educación) sobre el mismo Core.

## 9. Página Web

Una sola página comercial de DOOIF (los productos pueden tener landing propia,
pero siempre bajo el paraguas DOOIF). Estructura propuesta:

1. **Hero:** "DOOIF no vende IA. Vende conocimiento." Subtítulo: "Tu empresa,
   con motores que atienden, venden, cotizan y detectan oportunidades 24/7."
   CTA: agendar demo (atendida por un agente DOOIF: la demo es el producto).
2. **El problema:** el conocimiento de tu empresa está atrapado en documentos
   y en la cabeza de tu gente; solo trabaja cuando alguien está disponible.
3. **La plataforma:** DOOIF Core en un diagrama simple (conocimiento → motores
   → resultados), con los principios de reutilización y acumulación.
4. **Productos:** Sinergia, Agente Contactos, Licitaciones — cada uno con su
   resultado concreto ("no pierdas ninguna llamada", "no pierdas ninguna
   licitación").
5. **Casos:** un caso por motor, con números del cliente.
6. **Modelo:** proyecto a medida o suscripción; qué incluye cada camino.
7. **CTA final** + contacto por los propios canales de la plataforma (el chat
   web de la página es el chat embebible del Core — comer nuestra propia
   comida).

## 10. Pitch

**Elevator (10 segundos).**
"DOOIF convierte el conocimiento de tu empresa en motores que trabajan solos:
atienden, venden, cotizan y detectan oportunidades 24/7. No te vendemos IA; te
vendemos tu propio conocimiento, puesto a trabajar."

**Un minuto.**
"Las empresas ya tienen su activo más valioso: saben hacer su negocio. El
problema es que ese conocimiento solo trabaja cuando una persona está
disponible. DOOIF lo cambia: tomamos tus documentos, tus procesos y tu
experiencia, los cargamos en nuestra plataforma —DOOIF Core— y los conectamos
a motores especializados que actúan: un agente de voz que atiende y hace
llamadas, un motor que prospecta y hace seguimiento, uno que cotiza y cobra,
uno que vigila las licitaciones públicas y te avisa cuáles puedes ganar. Todo
sobre una sola plataforma cloud, sin instalar nada, y con una particularidad:
cada cliente hace más capaz la plataforma, así que cada mes DOOIF sabe hacer
más cosas por el mismo precio. No vendemos inteligencia artificial. Vendemos
conocimiento trabajando."

**Para inversionistas (el ángulo).**
Cada proyecto pagado deja un activo reutilizable en el Core: el costo de
desarrollo lo financian los clientes y el margen del producto SaaS crece con
cada vuelta. Es una plataforma acumulativa con recurrencia, no una consultora.

---

## Anexo — Estado actual (julio 2026)

| Pieza | Estado | Dónde vive |
|---|---|---|
| Motor de voz (STT→Claude→TTS, GSM/Twilio) | ✅ Producción fase 1 | repo `sinergia-voice` |
| WhatsApp Calling | 🔜 Fase 2 (señalización lista) | repo `sinergia-voice` |
| Prospección + outreach, seguimiento, cotizaciones, agenda, cobros, chat web | ✅ Módulos activos | repo `sinergia-voice` |
| SaaS multi-tenant (auth/RBAC, planes, white-label, superadmin) | ✅ Activo | repo `sinergia-voice` |
| Capa de conocimiento (embeddings, base vectorial, RAG como servicio) | 🔜 Por formalizar como servicio del Core | — |
| Motor de licitaciones | 🔜 Por construir | repo `licitaciones` (este) |
| Migración/estandarización AWS | 🔜 Pendiente (hoy Render) | — |

Este documento es un borrador vivo: las secciones de Historia (datos duros),
Roadmap (fechas) y Casos (números) requieren completarse por el equipo.
