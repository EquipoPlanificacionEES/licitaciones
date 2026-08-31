#!/usr/bin/env python3
"""Sonda de disponibilidad de las fuentes de datos de compra publica del Peru.

Correr desde una red con salida libre a *.gob.pe (no funciona detras del proxy
de egreso de las sesiones remotas). Solo hace GET, no descarga volumen: pide los
primeros bytes de cada recurso y reporta que respondio.

    python3 scripts/probe_seace.py                 # sonda todo
    python3 scripts/probe_seace.py --guardar out/  # ademas guarda las muestras

Lo que hay que mirar en la salida:
  - OCDS API y /descargas responden 200 y devuelven JSON  -> fase 1 desbloqueada
  - prod6 (buscador nuevo) responde                       -> revisar sus XHR
  - el buscador clasico responde HTML con ViewState       -> confirma JSF/captcha
"""

import argparse
import os
import sys
import urllib.error
import urllib.request

TIMEOUT = 30
UA = "Mozilla/5.0 (compatible; sonda-viabilidad/1.0)"
MAX_MUESTRA = 4096

FUENTES = [
    ("OCDS  portal",        "https://contratacionesabiertas.oece.gob.pe/"),
    ("OCDS  api",           "https://contratacionesabiertas.oece.gob.pe/api"),
    ("OCDS  descargas",     "https://contratacionesabiertas.oece.gob.pe/descargas"),
    ("OCDS  dominio viejo", "https://contratacionesabiertas.osce.gob.pe/api"),
    ("CONOSCE datos abiertos",
     "https://bi.seace.gob.pe/pentaho/api/repos/:public:portal:datosabiertos.html"
     "/content?userid=public&password=key"),
    ("CONOSCE convocatorias",
     "https://bi.seace.gob.pe/pentaho/api/repos/:public:portal:datosabiertosconvocatorias.html"
     "/content?userid=public&password=key"),
    ("CONOSCE PAC",
     "https://bi.seace.gob.pe/pentaho/api/repos/:public:portal:datosabiertospac.html"
     "/content?userid=public&password=key"),
    ("SEACE v3 buscador",
     "https://prod2.seace.gob.pe/seacebus-uiwd-pub/buscadorPublico/buscadorPublico.xhtml"),
    ("SEACE v3 buscador (prodapp2)",
     "https://prodapp2.seace.gob.pe/seacebus-uiwd-pub/buscadorPublico/buscadorPublico.xhtml"),
    ("SEACE nuevo (Ley 32069)", "https://prod6.seace.gob.pe/buscador-publico"),
    ("SEACE contratos",         "https://prod4.seace.gob.pe/contratos/publico/"),
    ("OCP Data Registry",       "https://data.open-contracting.org/en/publication/135"),
]

# Pistas que delatan la tecnologia y las fricciones de cada portal.
PISTAS = [
    ("javax.faces.ViewState", "JSF/PrimeFaces: hay estado de sesion por request"),
    ("captcha",               "captcha presente en la pagina"),
    ("recaptcha",             "reCAPTCHA presente"),
    ("ocid",                  "payload OCDS (trae ocid)"),
    ("releasePackage",        "release package OCDS"),
    ("recordPackage",         "record package OCDS"),
    ("<app-root",             "SPA Angular: la busqueda va por XHR a un servicio JSON"),
    ("main.js",               "SPA con bundle JS: revisar los XHR en DevTools"),
]


def sondear(nombre, url, destino=None):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            codigo, tipo, cuerpo = r.status, r.headers.get("Content-Type", "?"), r.read(MAX_MUESTRA)
    except urllib.error.HTTPError as e:
        codigo, tipo, cuerpo = e.code, e.headers.get("Content-Type", "?"), e.read(MAX_MUESTRA)
    except Exception as e:  # DNS, TLS, timeout, proxy
        print(f"  {nombre:32s} FALLO   {type(e).__name__}: {e}")
        return False

    texto = cuerpo.decode("utf-8", "replace")
    marcas = [d for p, d in PISTAS if p.lower() in texto.lower()]
    print(f"  {nombre:32s} {codigo}     {tipo.split(';')[0]:28s} {len(cuerpo)}+ bytes")
    for m in marcas:
        print(f"  {'':32s}       -> {m}")

    if destino:
        os.makedirs(destino, exist_ok=True)
        archivo = os.path.join(destino, nombre.replace(" ", "_").replace("/", "-") + ".txt")
        with open(archivo, "w", encoding="utf-8") as f:
            f.write(f"{url}\n{codigo} {tipo}\n\n{texto}")
    return 200 <= codigo < 400


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--guardar", metavar="DIR", help="guardar las muestras en DIR")
    args = ap.parse_args()

    if os.environ.get("HTTPS_PROXY"):
        print(f"aviso: HTTPS_PROXY={os.environ['HTTPS_PROXY']} — si es un proxy con "
              "politica de egreso, todo va a fallar con 403.\n")

    print("Sondeando fuentes de compra publica del Peru\n")
    vivos = sum(sondear(n, u, args.guardar) for n, u in FUENTES)
    print(f"\n{vivos}/{len(FUENTES)} fuentes respondieron.")
    print("\nSiguiente paso manual (10 min, define la arquitectura de tiempo real):")
    print("  abrir https://prod6.seace.gob.pe/buscador-publico con DevTools > Network,")
    print("  hacer una busqueda y anotar: URL del servicio, metodo, filtros,")
    print("  paginacion, forma de la respuesta y si exige captcha o token.")
    return 0 if vivos else 1


if __name__ == "__main__":
    sys.exit(main())
