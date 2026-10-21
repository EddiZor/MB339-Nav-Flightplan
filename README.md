# MB339-Nav-Flightplan

**MB339-Nav-Flightplan** è un'utility open-source sviluppata in Python e dotata di interfaccia grafica (GUI), progettata specificamente per **Microsoft Flight Simulator**. L'applicazione si collega in tempo reale al tuo account **SimBrief** per scaricare e analizzare l'ultimo piano di volo (OFP), interfacciandosi con il simulatore tramite **SimConnect** per guidare automaticamente l'Aermacchi MB-339 di IndiaFoxtEcho lungo la rotta impostando l'Heading bug dell'autopilota.

---

## Caratteristiche Principali
* **Integrazione Remota con SimBrief:** Recupera automaticamente tutti i waypoint, l'aeroporto di partenza e di arrivo dall'API XML di SimBrief inserendo semplicemente il tuo Pilot ID (con mascheramento automatico di sicurezza dopo 3 secondi).
* **Display Telemetria in Stile Avionica:** Mostra in tempo reale il waypoint attivo, la prua magnetica/geografica da tenere (`BRG`) e la distanza esatta in Miglia Nautiche (`NM`) calcolata tramite la formula di Haversine.
* **Ponte nativo con MSFS (SimConnect):** Monitora le coordinate GPS dell'aereo e invia i comandi di correzione dell'Heading all'autopilota in modo fluido.
* **Gestione Flessibile della Rotta:** Consente di avanzare o retrocedere manualmente tra i waypoint (`<< WP Prec.` / `WP Succ. >>`) o attivare/disattivare la navigazione automatica con un clic.
* **Guida Rapida Integrata (HOW TO):** Finestra informativa a scomparsa affiancata alla schermata principale con tutte le istruzioni operative per il cockpit.

---

## Requisiti di Sistema
* Microsoft Flight Simulator (MSFS 2020 / MSFS 2024)
* Aermacchi MB-339 (IndiaFoxtEcho)
* Python 3.9+ (se esegui lo script da codice sorgente)

---

