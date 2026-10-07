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

## Su Community Cloud l'app sta dentro una cornice

Questa e' la cosa da sapere prima di toccare qualunque riga qui sotto, ed e'
la ragione per cui su iPhone usciva l'icona di Streamlit.

Aprendo https://masterconegliano.streamlit.app la pagina in cima **non e'**
l'app. E' il guscio di Streamlit Community Cloud, con i suoi asset sotto
`/-/build/`, e dentro c'e' un iframe:

    <iframe src="https://masterconegliano.streamlit.app/~/+/">

Dentro quell'iframe gira la nostra app. Il guscio porta in testa i suoi tag:

    <link rel="apple-touch-icon" href="/-/build/favicon_256.png">
    <link rel="manifest" href="/-/build/manifest.json">   (name: "Streamlit")

`favicon_256.png` e' il logo di Streamlit, ed e' esattamente quello che Safari
prende quando fai "Aggiungi a Home", perche' Safari guarda il documento in
cima, non quello dentro la cornice.

Due conseguenze, verificate a mano sulla pagina live:

1. iniettare i tag in `window.parent.document` non serve a niente: quello e'
   il documento dell'app, dentro l'iframe, dove nessun browser va a cercare
   l'icona della home. Serve **`window.top.document`**. Per fortuna guscio,
   app e componente stanno tutti sulla stessa origine e l'iframe dell'app ha
   `allow-same-origin`, quindi da qui ci si arriva.
2. dal documento in cima il percorso dei nostri file **non** e'
   `/app/static/...`, che risponde 200 con l'HTML del guscio, ma
   `/~/+/app/static/...`, che risponde `image/png`. Il prefisso si ricava a
   runtime dal pathname della cornice, cosi' in locale, dove la cornice non
   c'e', resta `/app/static/`.

Misurato sulla pagina vera:

| richiesta | risposta |
|---|---|
| `/app/static/apple-touch-icon.png` | 200 `text/html` 9782 byte (il guscio) |
| `/~/+/app/static/apple-touch-icon.png` | 200 `image/png` 7748 byte |

Resta un limite su cui da dentro l'app non si puo' fare nulla: l'HTML del
guscio lo serve Streamlit, non noi, quindi i nostri tag arrivano comunque
dopo, via JavaScript. Se Safari decidesse l'icona solo al momento in cui
analizza la pagina, l'unica strada sarebbe uscire da Community Cloud.

Se cambi le icone: stessi nomi dentro static/, PNG opachi (iOS riempie di
nero il trasparente), angoli dritti (li arrotonda il sistema). La misura che
conta per la home di iOS e' `apple-touch-icon.png`, 180x180. Poi sul telefono
togli l'app dalla home e riaggiungila, perche' iOS tiene l'icona in cache.
"""
from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

TITOLO = "Master Conegliano"
COLORE = "#0a1628"


def _base() -> str:
    """Prefisso del sito, vuoto oppure '/sottocartella', mai con slash finale."""
    try:
        b = (st.get_option("server.baseUrlPath") or "").strip("/")
    except Exception:
        b = ""
    return f"/{b}" if b else ""


_JS = """
<script>
(function () {
  try {
    // 1. Il documento in cima, non quello dell'app. Su Community Cloud sono
    //    due cose diverse e l'icona della home la decide quello in cima.
    var doc = null;
    try { if (window.top && window.top.document) doc = window.top.document; } catch (e) {}
    if (!doc) { try { doc = window.parent.document; } catch (e) {} }
    if (!doc) return;

    // 2. Il prefisso della cornice. Community Cloud serve l'app dentro un
    //    iframe su /~/+/ e i nostri file stanno sotto quel prefisso anche per
    //    il documento in cima. In locale la cornice non c'e'.
    var cornice = '__BASE__/';
    try {
      var p = window.parent.location.pathname;
      var i = p.indexOf('/~/+/');
      if (i >= 0) cornice = p.slice(0, i + 5);
    } catch (e) {}
    var stat = cornice + 'app/static/';

    // 3. viewport-fit=cover sempre, anche quando i tag ci sono gia': senza,
    //    in standalone su iPhone resta una fascia bianca sotto la notch.
    var vp = doc.querySelector('meta[name="viewport"]');
    if (vp) {
      var c = vp.getAttribute('content') || '';
      if (c.indexOf('viewport-fit') === -1) {
        vp.setAttribute('content', c + ', viewport-fit=cover');
      }
    }

    // 4. Via i tag del guscio. Di manifest e apple-touch-icon il browser ne
    //    considera uno solo, e quello di Streamlit punta al suo logo. Si
    //    rifa' a ogni giro, cosi' se il guscio li rimette vengono ritolti.
    var vecchi = doc.querySelectorAll('link[rel="manifest"],' +
      ' link[rel~="apple-touch-icon"], link[rel~="apple-touch-icon-precomposed"]');
    for (var k = 0; k < vecchi.length; k++) {
      if (vecchi[k].getAttribute('data-rz') !== '1') vecchi[k].remove();
    }

    if (doc.getElementById('rz-pwa-manifest')) return;   // i nostri ci sono gia'

    var pezzi = doc.createDocumentFragment();
    function aggiungi(tag, attrs) {
      var n = doc.createElement(tag);
      n.setAttribute('data-rz', '1');
      for (var a in attrs) n.setAttribute(a, attrs[a]);
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
    components.html(
        _JS.replace("__BASE__", _base())
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
