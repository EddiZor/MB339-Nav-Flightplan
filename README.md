# MB339-Nav-Flightplan


## 🚀 Novità della Versione 3.0

L'aggiornamento alla versione 3.0 introduce importanti novità per il monitoraggio del volo, la gestione della rotta e l'usabilità dell'interfaccia:

*   **Pannello Telemetria Avanzata:** Aggiunto un nuovo display dinamico in alto a destra per il monitoraggio in tempo reale dei parametri di volo essenziali. Ora include:
    *   **TAS** (True Airspeed in Nodi)
    *   **GS** (Ground Speed in Nodi)
    *   **ALT** (Altitudine attuale in Piedi)
    *   **WIND** (Direzione e intensità del vento, es. 270°/15)
    *   **MACH** (Numero di Mach)
*   **Inversione Rotta (Reverse Plan):** Introdotto un pulsante dedicato ("Inverti Rotta") che permette di capovolgere istantaneamente il piano di volo caricato. Inverte l'ordine dei waypoint e scambia Partenza e Destinazione. È protetto da un pop-up di conferma per evitare clic accidentali.
*   **Gestione Sicura del SimBrief ID:** L'ID utente di SimBrief non è più inserito nel codice. Viene ora salvato localmente in un file di configurazione automatico (`mb339_nav_config.json`). Mantiene la mascheratura di sicurezza (asterischi) dopo l'inserimento per garantire la privacy, risultando ideale per chi fa streaming.
*   **Interfaccia Dinamica Espansiva (UI):** Il layout dei pannelli digitali stile "LED" è stato riprogettato. Ora i riquadri sfruttano dinamicamente tutta la larghezza orizzontale della finestra. Le dimensioni dei font sono state notevolmente ingrandite per garantire una lettura immediata dei parametri (ETE, EFOB, XTK, ecc.) a colpo d'occhio.
*   **Integrazione Discord:** Aggiunto un pulsante diretto nella barra superiore per accedere istantaneamente al server Discord della community **SKYSIM PILOT**.


MB339-Nav-Flightplan ✈️ (v2.3)

An external GPS navigation and flight plan (SimBrief & .PLN) utility designed specifically for the IndiaFoxtEcho MB-339 in Microsoft Flight Simulator.

Since the MB-339 lacks an internal moving map or standard GPS, this lightweight desktop companion acts as your digital navigator, connecting directly to the simulator's autopilot via SimConnect.

🚀 What's New in Version 2.3 (The Ultimate Navigation Upgrade)

Auto-Sync Waypoint: The app intelligently analyzes your current aircraft position upon connection and automatically selects the correct active flight plan leg. No more routing back to the departure airport if you restart the app mid-flight!

Live ETE & EFOB: Added real-time calculation for Estimated Time Enroute and Estimated Fuel On Board (in KG) to your final destination, based on current ground speed and engine fuel flow.

Cross-Track Error (XTK): A new XTK indicator (in NM) helps you monitor course deviation. The value turns red to alert you if you drift off the ideal flight path by more than 2.0 NM.

Dynamic & Responsive UI: The main display has been enlarged and dynamically adjusts to perfectly distribute telemetry data.

Non-Blocking UI & Thread-Safe Telemetry: Network requests (SimBrief) and real-time MSFS telemetry are fully synchronized in the background, eliminating crashes and UI freezes.

Smart SimConnect Handling: The application gracefully detects unexpected MSFS disconnections without crashing.

🌟 Key Features

Seamless SimBrief Integration: Fetch your operational flight plan (OFP) directly using your SimBrief Pilot ID.

Local .PLN Support: Load standard MSFS 2020/2024 or Little Navmap flight plans with full coordinate parsing.

Automatic Navigation (HDG Sync): Calculates real-time bearing and automatically syncs the Heading Bug on the MB-339's HSI. It sequences to the next waypoint automatically when within 0.8 NM.

Bilingual Interface: Fully supports English and Italian UI.

📥 Download & Installation

Download the latest MB339-Nav-Flightplan-v2.3.zip from the GitHub Releases page.

Extract the ZIP archive to a folder of your choice.

Run MB339-Nav-Flightplan.exe (No installation required).

🛠️ How to Use (Cockpit Setup)

Load Route: Enter your SimBrief ID and click Fetch OFP, or click Load .PLN for local files.

Connect: Click Connect MSFS.

Aircraft Setup: Turn on electrical power/avionics in your MB-339.

Autopilot ON: Engage the Autopilot Master (ON) on the glareshield panel.

HDG Mode: Press the HDG button on the aircraft's autopilot panel.

Start Navigation: Click START NAV (HDG) on the desktop app. The utility will take over and guide the aircraft to the destination!


# MB339-Nav-Flightplan ✈️ (v2.0)


## 🚀 What's New in Version 2.0
* **Non-Blocking UI:** Network requests (SimBrief) and file parsing are now handled in the background. The app no longer freezes during data fetching.
* **Thread-Safe Telemetry:** Real-time MSFS telemetry and UI updates are fully synchronized, eliminating crashes and race conditions.
* **Smart SimConnect Handling:** The application now gracefully detects and handles unexpected MSFS disconnections without crashing.


An external GPS navigation and flight plan (SimBrief & .PLN) utility designed specifically for the IndiaFoxtEcho MB-339 in Microsoft Flight Simulator.

**MB339-Nav-Flightplan** is a lightweight open-source utility developed in Python with a modern dark-avionics GUI, designed specifically for **Microsoft Flight Simulator (2020 & 2024)** and tailored for the IndiaFoxtEcho **Aermacchi MB-339**.

---

## 🌐 English / Italiano

### 🚀 Key Features (EN)
* **Dual Route Loading (SimBrief & .PLN files):** Fetch your latest SimBrief OFP via Pilot ID (with automatic masking after 3 seconds) or load any local `.pln` flight plan file compatible with MSFS 2020 / MSFS 2024.
* **Avionics LED Telemetry Display:** Real-time display of the active waypoint, heading bearing (`BEARING`), exact distance in nautical miles (`DISTANCE NM`) calculated via Haversine formula, and airport ICAO codes for Departure (`DEP`) and Destination (`DEST`).
* **Native MSFS Bridge (SimConnect):** Continuously monitors aircraft GPS coordinates and smoothly steers the autopilot *Heading Bug*.
* **Secure Route Management:** Step forward or backward through waypoints using dedicated buttons (`<< Prev WP` / `Next WP >>`). Manual table clicking is disabled to prevent accidental route changes in flight.
* **Integrated Guide (HOW TO):** Quick reference window with cockpit setup instructions.
* **Custom GPS Icon & Standalone Executable:** Includes a custom vector-style icon embedded in both the UI and the compiled `.exe`.

---

### 🚀 Caratteristiche Principali (IT)
* **Doppia Modalità di Caricamento Rotta (SimBrief & File .PLN):** Scarica l'ultimo OFP da SimBrief tramite Pilot ID (con mascheramento automatico di sicurezza) oppure carica qualsiasi file `.pln` locale per MSFS 2020 / MSFS 2024.
* **Display Telemetria LED Avionico:** Visualizza in tempo reale il waypoint attivo, la prua da mantenere (`BEARING`), la distanza in Miglia Nautiche (`DISTANCE NM`) e i codici ICAO di Partenza (`DEP`) e Arrivo (`DEST`).
* **Ponte Nativo MSFS (SimConnect):** Monitora costantemente le coordinate GPS dell'aereo e invia i comandi di correzione della prua all'autopilota.
* **Gestione Rotta Sicura:** Avanza o retrocedi tra i waypoint usando esclusivamente i pulsanti dedicati (`<< WP Prec.` / `WP Succ. >>`). La selezione manuale tramite clic sulla tabella è bloccata per sicurezza.
* **Guida Rapida Integrata (HOW TO):** Finestra informativa con le istruzioni di configurazione nel cockpit.
* **Icona GPS & Eseguibile Standalone:** Include un'icona personalizzata integrata sia nell'interfaccia che nell'eseguibile `.exe`.

---

## 📋 System Requirements / Requisiti di Sistema
* **Microsoft Flight Simulator** (MSFS 2020 / MSFS 2024)
* **Aermacchi MB-339** (IndiaFoxtEcho)
* **Python 3.9+** (only required if running from source code / necessario solo se si esegue da codice sorgente)

---

## 🛠️ Installation & Usage (Source Code)

1. Clone or download the repository to your local working directory.
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## 📥 Download & Installation
1. Download the latest `MB339-Nav-Flightplan-v2.0.zip` from the [GitHub Releases](https://github.com/EddiZor/MB339-Nav-Flightplan/releases/latest) page or from [Flightsim.to](INSERISCI_QUI_IL_TUO_LINK_FLIGHTSIM).
2. Extract the ZIP archive to a folder of your choice.
3. Run `MB339-Nav-Flightplan.exe` (No installation required).

---

## 📦 Building the Standalone Executable (.exe)

The project includes an automated compilation script (`build_exe.py`) that cleans cache, generates the `.ico` icon, and bundles the native `SimConnect.dll` library:

1. Open your terminal in the project folder and run:
   ```bash
   python build_exe.py
   ```
2. Find your compiled executable in the `dist/` folder:
   `dist/MB339-Nav-Flightplan.exe`

---

## ✈️ Cockpit Operating Instructions (MB-339)

### 1. Autopilot & Flight Director Setup
* Turn on the aircraft electrical power and avionics.
* Locate the Flight Director / Autopilot panel on the central glareshield.
* Ensure the Autopilot is engaged (`Master ON`).
* Press the **`HDG`** (Heading) button to let the application control the heading bug.
* To hold your cruise level, engage **`ALT HOLD`** once you reach your desired altitude.

### 2. Starting Navigation
* Launch the application (`MB339-Nav-Flightplan.exe`).
* Enter your **SimBrief Pilot ID** and click **`Fetch OFP`**, or click **`Load .PLN`** to import a local flight plan.
* Click **`Connect MSFS`** to establish communication with the simulator.
* Click the center button **`START NAV (HDG)`**: the system will automatically steer the aircraft along the route waypoints, sequencing to the next point when within `0.8 NM`.

---

Developed by **Eddi Zorzini** (`EddiZor`)