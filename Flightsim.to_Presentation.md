# ✈ MB339-Nav-Flightplan

**MB339-Nav-Flightplan** is a lightweight external utility developed in Python with a modern dark-avionics GUI, designed specifically for **Microsoft Flight Simulator (2020 & 2024)** and tailored for the IndiaFoxtEcho **Aermacchi MB-339**.

---

## 🌐 English / Italiano

### 🚀 Key Features (EN)
* **Dual Route Loading:** Fetch your active flight plan directly from **SimBrief** using your Pilot ID (with auto-masking security) or load any local **`.pln`** file (fully compatible with MSFS 2020 and MSFS 2024 formats).
* **Avionics LED Telemetry Display:** Real-time digital display showing the active waypoint, heading bearing (`BEARING`), precise distance in nautical miles (`DISTANCE NM`) via Haversine calculation, and airport ICAO codes for Departure (`DEP`) and Destination (`DEST`).
* **Native MSFS Bridge (SimConnect):** Continuously monitors your aircraft's GPS coordinates and automatically steers the autopilot *Heading Bug* along your route.
* **Secure Route Control:** Step forward or backward through your route using dedicated buttons (`<< Prev WP` / `Next WP >>`). Table clicking is locked to prevent accidental route changes during flight.
* **Integrated Guide (HOW TO):** Quick reference window with complete cockpit setup instructions.
* **Bilingual UI:** Instantly switch between English and Italian at any time with dedicated flag buttons.

---

### 🚀 Caratteristiche Principali (IT)
* **Doppia Modalità Rotta:** Importa il piano di volo da **SimBrief** tramite Pilot ID (con mascheramento automatico di sicurezza) oppure carica qualsiasi file **`.pln`** locale (compatibile con MSFS 2020 e MSFS 2024).
* **Display Telemetria LED Avionico:** Pannello digitale in tempo reale con waypoint attivo, prua (`BEARING`), distanza in Miglia Nautiche (`DISTANCE NM`) e codici ICAO di Partenza (`DEP`) e Arrivo (`DEST`).
* **Ponte Nativo MSFS (SimConnect):** Monitora costantemente la posizione GPS e pilota automaticamente l'*Heading Bug* dell'autopilota.
* **Gestione Rotta Sicura:** Avanza o retrocedi tra i waypoint usando esclusivamente i pulsanti dedicati (`<< WP Prec.` / `WP Succ. >>`). Clic sulla tabella disabilitato per sicurezza in volo.
* **Guida Rapida Integrata (HOW TO):** Finestra con le istruzioni di configurazione nel cockpit.
* **Interfaccia Bilingue:** Selettore rapido integrato tra Inglese e Italiano.

---

## 📋 System Requirements / Requisiti
* **Microsoft Flight Simulator** (MSFS 2020 or MSFS 2024)
* **Aermacchi MB-339** (IndiaFoxtEcho)
* Windows 10 / 11

---

## 📦 Installation / Installazione
1. Download the `.zip` archive.
2. Extract the `MB339-Nav-Flightplan.exe` anywhere on your computer.
3. Run the executable while MSFS is open.

---

## ✈️ Cockpit Operating Instructions (MB-339)

1. **Autopilot Setup:** Turn on electrical power and avionics. Ensure the Autopilot is engaged (`Master ON`) and press the **`HDG`** (Heading) button on the glareshield panel. Engage **`ALT HOLD`** for cruise altitude.
2. **Load Route:** Enter your SimBrief Pilot ID and click **`Fetch OFP`**, or click **`Load .PLN`** to open a local flight plan.
3. **Connect:** Click **`Connect MSFS`** to establish SimConnect communication.
4. **Start Navigation:** Click **`START NAV (HDG)`** and enjoy your flight! The system will automatically sequence to the next waypoint when within `0.8 NM`.

---
Developed by **Eddi Zorzini** (`EddiZor`)