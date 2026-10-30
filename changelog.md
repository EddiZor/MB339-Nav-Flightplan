## 🚀 What's New in Version 3.0

The 3.0 update introduces major enhancements for flight monitoring, route management, and user interface usability:

*   **Advanced Telemetry Panel:** Added a new dynamic display in the top right corner for real-time monitoring of essential flight parameters. It now includes:
    *   **TAS** (True Airspeed in Knots)
    *   **GS** (Ground Speed in Knots)
    *   **ALT** (Current Altitude in Feet)
    *   **WIND** (Wind direction and velocity, e.g., 270°/15)
    *   **MACH** (Mach Number)
*   **Reverse Route (Reverse Plan):** Introduced a dedicated button ("Reverse Plan") that instantly flips the loaded flight plan. It reverses the order of the waypoints and swaps Departure and Destination. It's protected by a confirmation pop-up to prevent accidental clicks.
*   **Secure SimBrief ID Management:** The SimBrief user ID is no longer hardcoded. It is now saved locally in an automatic configuration file (`mb339_nav_config.json`). It retains the security masking (asterisks) after input to ensure privacy, making it ideal for streamers.
*   **Expansive Dynamic Interface (UI):** The layout of the digital "LED" style panels has been redesigned. The frames now dynamically utilize the entire horizontal width of the window. Font sizes have been significantly enlarged to ensure immediate reading of parameters (ETE, EFOB, XTK, etc.) at a glance.
*   **Discord Integration:** Added a direct button in the top bar to instantly access the **SKYSIM PILOT** community Discord server.

---

**Changelog Version 3.0**

**New Features**
* Added the real-time Advanced Telemetry panel with indications for True Airspeed (TAS), Ground Speed (GS), Altitude (ALT), Wind (Direction/Velocity), and Mach Number.
* Implemented the "Reverse Plan" button with a confirmation window, allowing you to swap origin and destination by reversing the waypoint order.
* Introduced automatic saving of the SimBrief ID to a local file (`mb339_nav_config.json`), eliminating the need to type credentials at every launch.
* Integrated a direct button in the top bar to access the SKYSIM PILOT community Discord server.
* Finalized advanced route calculations: Estimated Time Enroute (ETE), Estimated Fuel On Board (EFOB in KG), Cross-Track Error (XTK), and the Auto-Sync algorithm for automatic in-flight position recognition.

**UI and UX Improvements**
* Dynamic redesign of the digital panels (avionics LED style): frames now use the full horizontal width of the window.
* Significant increase in font sizes (headers to 11pt, telemetry values to 20pt, route values to 26pt) for immediate readability during simulation.
* Optimized SimBrief ID masking, which now hides characters with asterisks even when the ID is automatically loaded from the configuration file.
* Repositioned the status label ("Status: Connected/Disconnected") to accommodate the new buttons without overlap.

**Bug Fixes**
* Resolved an `IndentationError` in the UI update block within the `sim_loop()` method.
* Fixed the omission of the status bar that prevented the correct loading of `.pln` files and SimBrief plans.





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

---

**Changelog Versione 3.0**

**Nuove Funzionalità**
* Aggiunto il pannello Telemetria Avanzata in tempo reale con indicazioni di True Airspeed (TAS), Ground Speed (GS), Altitudine (ALT), Vento (Direzione/Intensità) e Numero di Mach.
* Implementato il pulsante "Inverti Rotta" (Reverse Plan) con finestra di conferma, che permette di scambiare origine e destinazione invertendo l'ordine dei waypoint.
* Introdotto il salvataggio automatico dell'ID SimBrief in un file locale (`mb339_nav_config.json`), eliminando la necessità di digitare le credenziali a ogni avvio.
* Integrato un pulsante diretto nella barra superiore per l'accesso al server Discord della community SKYSIM PILOT.
* Finalizzati i calcoli avanzati di rotta: Estimated Time Enroute (ETE), Estimated Fuel On Board (EFOB in KG), Cross-Track Error (XTK) e l'algoritmo Auto-Sync per il riconoscimento automatico della posizione in volo.

**Miglioramenti Interfaccia e UX**
* Riprogettazione dinamica dei pannelli digitali (stile LED avionico): i riquadri sfruttano ora l'intera larghezza orizzontale della finestra.
* Aumento significativo delle dimensioni dei font (intestazioni a 11pt, valori telemetrici a 20pt, valori di rotta a 26pt) per una lettura immediata durante la simulazione.
* Ottimizzata la mascheratura dell'ID SimBrief, che ora nasconde i caratteri con asterischi anche quando l'ID viene caricato in automatico dal file di configurazione.
* Riposizionata la label di stato ("Status: Connected/Disconnected") per accomodare i nuovi pulsanti senza sovrapposizioni.

**Correzioni (Bug Fixes)**
* Risolto un `IndentationError` nel blocco di aggiornamento UI all'interno del metodo `sim_loop()`.
* Corretta l'omissione della barra di stato che impediva il corretto caricamento dei file `.pln` e dei piani SimBrief.