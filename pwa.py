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
"""
from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

_JS = """
<script>
(function () {
  try {
    var doc = window.parent.document;
    if (!doc || doc.getElementById('rz-pwa-manifest')) return;

    var base = window.parent.location.pathname.replace(/\\/+$/, '');
    var stat = base + '/app/static/';

    function meta(attrs) {
      var m = doc.createElement('meta');
      for (var k in attrs) m.setAttribute(k, attrs[k]);
      doc.head.appendChild(m);
    }

    var link = doc.createElement('link');
    link.id = 'rz-pwa-manifest';
    link.rel = 'manifest';
    link.href = stat + 'manifest.json';
    doc.head.appendChild(link);

    var icon = doc.createElement('link');
    icon.rel = 'apple-touch-icon';
    icon.setAttribute('sizes', '192x192');
    icon.href = stat + 'icon-192.png';
    doc.head.appendChild(icon);

    meta({name: 'apple-mobile-web-app-capable', content: 'yes'});
    meta({name: 'mobile-web-app-capable', content: 'yes'});
    meta({name: 'apple-mobile-web-app-status-bar-style', content: 'black-translucent'});
    meta({name: 'apple-mobile-web-app-title', content: 'Master Conegliano'});
    meta({name: 'theme-color', content: '#0a1628'});

    // viewport con viewport-fit=cover: senza, in standalone su iPhone
    // resta una fascia bianca sotto la notch
    var vp = doc.querySelector('meta[name="viewport"]');
    if (vp) {
      var c = vp.getAttribute('content') || '';
      if (c.indexOf('viewport-fit') === -1) {
        vp.setAttribute('content', c + ', viewport-fit=cover');
      }
    }
  } catch (e) {
    // origine diversa o DOM non accessibile: l'app funziona lo stesso
  }
})();
</script>
"""


def enable() -> None:
    """Inietta manifest e meta tag nella pagina. Da chiamare una volta per rerun."""
    components.html(_JS, height=0, width=0)


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
