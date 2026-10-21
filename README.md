# MB339-Nav-Flightplan

**MB339-Nav-Flightplan** è un'utility open-source sviluppata in Python e dotata di un'interfaccia grafica (GUI) in stile avionica, progettata specificamente per **Microsoft Flight Simulator**. 

L'applicazione si collega in tempo reale al tuo account **SimBrief** per scaricare e analizzare l'ultimo piano di volo (OFP) via XML, interfacciandosi con il simulatore tramite **SimConnect** per guidare automaticamente l'Aermacchi MB-339 di IndiaFoxtEcho lungo la rotta, pilotando l'Heading bug dell'autopilota in tempo reale.

---

## 🚀 Caratteristiche Principali

* **Integrazione Remota SimBrief:** Recupera automaticamente waypoint, partenze e arrivi dall'API XML di SimBrief inserendo il tuo Pilot ID (con mascheramento di sicurezza tramite asterischi dopo 3 secondi).
* **Display Telemetria Avionica:** Visualizza in tempo reale il waypoint attivo, la prua magnetica/geografica da tenere (`BRG`) e la distanza esatta in Miglia Nautiche (`NM`) calcolata con la formula di Haversine.
* **Ponte Nativo MSFS (SimConnect):** Monitora le coordinate GPS dell'aereo e invia i comandi di correzione della prua all'autopilota in modo fluido e continuo.
* **Gestione Rotta Flessibile:** Permette di avanzare o retrocedere tra i punti di passaggio utilizzando esclusivamente i pulsanti dedicati (`<< WP Prec.` / `WP Succ. >>`). La selezione manuale tramite clic sulla tabella è disattivata per evitare selezioni accidentali in volo.
* **Guida Rapida Integrata (HOW TO):** Finestra informativa affiancata alla schermata principale con tutte le istruzioni operative e il setup specifico per il cockpit dell'MB-339.
* **Icona GPS & Eseguibile Standalone:** Include un'icona vettoriale personalizzata a tema avionica/GPS sia nell'interfaccia che nell'eseguibile compilato.

---

## 📋 Requisiti di Sistema

* **Microsoft Flight Simulator** (MSFS 2020 / MSFS 2024)
* **Aermacchi MB-339** (IndiaFoxtEcho)
* **Python 3.9+** (se si esegue lo script da codice sorgente)

---

## 🛠️ Installazione e Utilizzo (Da Codice Sorgente)

1. Clona o scarica il repository nella tua cartella di lavoro locale.
2. Installa le dipendenze richieste tramite il terminale:
   ```bash
   pip install -r requirements.txt
