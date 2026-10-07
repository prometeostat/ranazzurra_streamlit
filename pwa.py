"""
pwa.py — rende l'app installabile sulla schermata home.

Cosa si ottiene davvero con Streamlit:
  - icona sulla home di iPhone/Android e apertura a schermo intero, senza
    barra del browser (manifest + meta tag Apple);
  - colore della status bar coerente col tema scuro;
  - niente funzionamento offline e niente notifiche push: servirebbe un
    service worker servito dalla radice del dominio, e Streamlit non permette
    di pubblicare file a quel livello ne' di toccare l'header
    Service-Worker-Allowed. Se un giorno servisse l'offline, la strada e' un
    frontend separato che legge un'API.

Requisiti: in .streamlit/config.toml deve esserci

    [server]
    enableStaticServing = true

cosi' la cartella static/ viene pubblicata sotto /app/static/.

## Perche' su iPhone usciva l'icona di Streamlit

La prima versione costruiva l'indirizzo delle icone da
`window.parent.location.pathname`. Sulla pagina di partenza funziona, perche'
il pathname e' `/`. Su qualsiasi altra pagina, Profilo compreso (dove stanno
proprio le istruzioni per installare l'app), il pathname e' `/profilo` e
l'indirizzo diventava `/profilo/app/static/icon-192.png`. Quell'indirizzo non
da' nemmeno 404: Streamlit e' una single page app e risponde **200 con
index.html**, cioe' HTML dove Safari si aspetta un PNG. Safari scarta il file
e ripiega sull'icona di default, che e' quella di Streamlit.

Verificato con un browser vero su una copia dell'app: dalla radice
`/app/static/icon-192.png` torna `image/png` di 7917 byte, da `/profilo` lo
stesso percorso torna `text/html` di 1837 byte.

Rimedi, in ordine di importanza:

1. l'indirizzo delle icone si calcola **qui in Python**, assoluto e uguale su
   tutte le pagine. Niente piu' indovinelli lato browser.
2. i tag vanno in cima alla `<head>` e quelli che competono (un altro
   manifest, un altro apple-touch-icon) vengono tolti: di quei due rel il
   browser ne considera uno solo, e non e' detto che scelga il nostro.
3. la misura buona per la home di iOS e' **180x180**, non 192: la dichiariamo
   per prima, con il PNG opaco dedicato.
4. `index.html` di Streamlit viene ritoccato una volta sola all'avvio, cosi' i
   tag ci sono gia' nell'HTML che Safari legge al primo colpo invece di
   arrivare dopo via JavaScript. La toppa e' marcata e idempotente, e se la
   cartella non e' scrivibile non succede niente: resta l'iniezione JS.
   Il link del manifest porta lo stesso `id` che cerca il JavaScript, cosi'
   quando la toppa c'e' l'iniezione si ferma subito e i tag non si sdoppiano.
   La primissima visita a container freddo arriva prima che lo script Python
   giri, quindi quella vede ancora l'HTML non toccato: li' lavora il JS.

Se cambi le icone: stessi nomi dentro static/, PNG opachi (iOS riempie di nero
il trasparente), angoli dritti (li arrotonda il sistema). Poi sul telefono
togli l'app dalla home e riaggiungila, perche' iOS tiene l'icona in cache.
"""
from __future__ import annotations

import shutil
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

TITOLO = "Master Conegliano"
COLORE = "#0a1628"

_MARCATORE = "<!-- rz-pwa -->"
_QUI = Path(__file__).resolve().parent


def _base() -> str:
    """Prefisso del sito, vuoto oppure '/sottocartella', mai con slash finale."""
    try:
        b = (st.get_option("server.baseUrlPath") or "").strip("/")
    except Exception:
        b = ""
    return f"/{b}" if b else ""


def _tag(stat: str) -> str:
    """I tag della head, gli stessi nel patch e nell'iniezione JavaScript."""
    return (
        f'{_MARCATORE}'
        f'<link rel="apple-touch-icon" sizes="180x180" '
        f'href="{stat}apple-touch-icon.png"/>'
        f'<link rel="apple-touch-icon-precomposed" sizes="180x180" '
        f'href="{stat}apple-touch-icon.png"/>'
        f'<link rel="apple-touch-icon" sizes="192x192" '
        f'href="{stat}icon-192.png"/>'
        f'<link rel="manifest" id="rz-pwa-manifest" href="{stat}manifest.json"/>'
        f'<meta name="apple-mobile-web-app-capable" content="yes"/>'
        f'<meta name="mobile-web-app-capable" content="yes"/>'
        f'<meta name="apple-mobile-web-app-status-bar-style" '
        f'content="black-translucent"/>'
        f'<meta name="apple-mobile-web-app-title" content="{TITOLO}"/>'
        f'<meta name="theme-color" content="{COLORE}"/>'
    )


def _patcha_index(stat: str) -> bool:
    """
    Mette i tag dentro l'index.html di Streamlit, una volta sola.

    Serve perche' Safari guarda le icone mentre analizza la pagina, e un tag
    aggiunto dopo con JavaScript a volte non lo vede. Copia anche l'icona
    Apple nella radice del sito, dove Safari la cerca per convenzione come
    ultima spiaggia, anche senza nessun tag.

    Tutto dentro un try: se la cartella di Streamlit e' in sola lettura l'app
    funziona lo stesso, con la sola iniezione JavaScript.
    """
    try:
        radice = Path(st.__file__).resolve().parent / "static"
        index = radice / "index.html"
        if not index.is_file():
            return False

        sorgente = _QUI / "static" / "apple-touch-icon.png"
        if sorgente.is_file():
            for nome in ("apple-touch-icon.png",
                         "apple-touch-icon-precomposed.png"):
                copia = radice / nome
                if (not copia.is_file()
                        or copia.stat().st_size != sorgente.stat().st_size):
                    shutil.copyfile(sorgente, copia)

        html = index.read_text(encoding="utf-8")
        if _MARCATORE in html:
            return True
        if "<head>" not in html:
            return False
        html = html.replace("<head>", "<head>" + _tag(stat), 1)
        # viewport-fit=cover sul viewport che c'e' gia': un secondo meta
        # viewport accanto al suo fa litigare i browser, meglio ritoccarlo.
        if "viewport-fit" not in html:
            html = html.replace(
                'content="width=device-width, initial-scale=1, shrink-to-fit=no"',
                'content="width=device-width, initial-scale=1, '
                'shrink-to-fit=no, viewport-fit=cover"', 1)
        index.write_text(html, encoding="utf-8")
        return True
    except Exception:
        return False


_JS = """
<script>
(function () {
  try {
    var doc = window.parent.document;
    if (!doc) return;

    // viewport-fit=cover sempre, anche quando i tag ci sono gia': senza,
    // in standalone su iPhone resta una fascia bianca sotto la notch.
    var vp = doc.querySelector('meta[name="viewport"]');
    if (vp) {
      var c = vp.getAttribute('content') || '';
      if (c.indexOf('viewport-fit') === -1) {
        vp.setAttribute('content', c + ', viewport-fit=cover');
      }
    }

    if (doc.getElementById('rz-pwa-manifest')) return;

    var stat = '__STATIC__';

    // Via i tag che competono con i nostri: di manifest e apple-touch-icon
    // il browser ne considera uno solo, e non e' detto che scelga il nostro.
    var vecchi = doc.querySelectorAll('link[rel="manifest"],' +
      ' link[rel~="apple-touch-icon"], link[rel~="apple-touch-icon-precomposed"]');
    for (var i = 0; i < vecchi.length; i++) vecchi[i].remove();

    var pezzi = doc.createDocumentFragment();
    function aggiungi(tag, attrs) {
      var n = doc.createElement(tag);
      for (var k in attrs) n.setAttribute(k, attrs[k]);
      pezzi.appendChild(n);
    }

    // 180x180 per prima: e' la misura che iOS vuole per la schermata home.
    aggiungi('link', {rel: 'apple-touch-icon', sizes: '180x180',
                      href: stat + 'apple-touch-icon.png'});
    aggiungi('link', {rel: 'apple-touch-icon-precomposed', sizes: '180x180',
                      href: stat + 'apple-touch-icon.png'});
    aggiungi('link', {rel: 'apple-touch-icon', sizes: '192x192',
                      href: stat + 'icon-192.png'});
    aggiungi('link', {rel: 'manifest', href: stat + 'manifest.json',
                      id: 'rz-pwa-manifest'});

    aggiungi('meta', {name: 'apple-mobile-web-app-capable', content: 'yes'});
    aggiungi('meta', {name: 'mobile-web-app-capable', content: 'yes'});
    aggiungi('meta', {name: 'apple-mobile-web-app-status-bar-style',
                      content: 'black-translucent'});
    aggiungi('meta', {name: 'apple-mobile-web-app-title', content: '__TITOLO__'});
    aggiungi('meta', {name: 'theme-color', content: '__COLORE__'});

    doc.head.insertBefore(pezzi, doc.head.firstChild);
  } catch (e) {
    // origine diversa o DOM non accessibile: l'app funziona lo stesso
  }
})();
</script>
"""


def enable() -> None:
    """Inietta manifest e meta tag nella pagina. Da chiamare una volta per rerun."""
    stat = f"{_base()}/app/static/"
    _patcha_index(stat)
    components.html(
        _JS.replace("__STATIC__", stat)
           .replace("__TITOLO__", TITOLO)
           .replace("__COLORE__", COLORE),
        height=0, width=0)


def install_hint() -> None:
    """Istruzioni brevi per aggiungere l'app alla schermata home."""
    st.markdown(
        """
        <div class="glass-card-accent" style="font-family:'Barlow Condensed',sans-serif;
             font-size:13px;color:var(--muted);line-height:1.7">
          <b style="color:var(--teal)">Installa l'app</b><br>
          <b>iPhone</b>: apri in Safari, tocca Condividi e poi "Aggiungi a Home".<br>
          <b>Android</b>: menu di Chrome, "Aggiungi a schermata Home".<br>
          Si apre a schermo intero come un'app. Serve la connessione: i dati
          arrivano dal database in tempo reale.
        </div>
        """,
        unsafe_allow_html=True,
    )
