import os
import sys
import re
import time
import math
import ctypes
import json
import threading
import webbrowser
import requests
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from SimConnect import *

# Imposta l'AppUserModelID su Windows affinché l'icona appaia nella barra delle applicazioni
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("eddizor.mb339.simbrief.nav")
except Exception:
    pass


TRANSLATIONS = {
    "IT": {
        "lang_btn": " EN",
        "discord_btn": "DISCORD",
        "fetch_ofp": "Scarica OFP",
        "load_pln": "Carica .PLN",
        "connect_msfs": "Connetti MSFS",
        "reconnect_msfs": "Riconnetti MSFS",
        "status_disc": "● Stato: Disconnesso da MSFS",
        "status_conn": "● Stato: Connesso a MSFS (SimConnect Attivo)",
        "status_err": "● Stato: Errore connessione MSFS",
        "status_loading": "● Stato: Download dati in corso...",
        "col_wp": "Waypoint",
        "col_lat": "Latitudine",
        "col_lon": "Longitudine",
        "col_dist": "Distanza (NM)",
        "col_dep": "DEP",
        "col_dest": "DEST",
        "col_ete": "ETE (DEST)",
        "col_efob": "EFOB (KG)",
        "col_xtk": "XTK (NM)",
        "prev_wp": "<< WP Prec.",
        "next_wp": "WP Succ. >>",
        "start_nav": "AVVIA NAV (HDG)",
        "stop_nav": "NAV ATTIVA (STOP)",
        "route_done": "ROTTA COMPLETATA",
        "exit": "ESCI",
        "howto_title": "HOW TO - MB-339 Cockpit Setup & Guida",
        "howto_header": "GUIDA OPERATIVA & COCKPIT SETUP",
        "howto_close": "CHIUDI GUIDA",
        "howto_text": (
            "1. CARICAMENTO ROTTA (SIMBRIEF O FILE .PLN):\n"
            "   • Da SimBrief: inserisci il tuo Pilot ID e clicca su 'Scarica OFP'.\n"
            "   • Da File Locale: clicca su 'Carica .PLN' e seleziona un file .pln\n"
            "     generato da MSFS 2024 / 2020, Little Navmap o SimBrief.\n"
            "   • Clicca su 'Connetti MSFS' per attivare il ponte SimConnect.\n\n"
            "2. SETUP NEL COCKPIT DELL'MB-339:\n"
            "   • Accendi l'impianto elettrico e l'avionica del velivolo.\n"
            "   • Individua il pannello del Flight Director / Autopilota sul glareshield.\n"
            "   • Assicurati che l'autopilota sia inserito (Master ON).\n"
            "   • Premi il pulsante HDG (Heading) per abilitare il controllo di prua.\n"
            "   • Se desideri mantenere la quota, inserisci ALT HOLD a quota di crociera.\n\n"
            "3. NAVIGAZIONE AUTOMATICA:\n"
            "   • Clicca su 'AVVIA NAV (HDG)' nell'applicazione.\n"
            "   • L'utility calcolerà in tempo reale il rilevamento (Bearing) e\n"
            "     aggiornerà automaticamente l'Heading Bug sul tuo HSI.\n"
            "   • Al raggiungimento del waypoint (sotto 0.8 NM), l'app passerà\n"
            "     in automatico al punto successivo fino a destinazione.\n\n"
            "4. GESTIONE MANUALE DELLA ROTTA:\n"
            "   • Usa esclusivamente i pulsanti '<< WP Prec.' e 'WP Succ. >>'\n"
            "     per cambiare il waypoint attivo in qualsiasi momento."
        ),
        "dlg_open_pln": "Seleziona Piano di Volo MSFS (.pln)",
        "dlg_all_files": "Tutti i file",
        "warn_title": "Attenzione",
        "warn_sb_id": "Inserisci il tuo SimBrief Pilot ID.",
        "warn_not_conn_title": "Non Connesso",
        "warn_not_conn_msg": "Connettiti prima a MSFS!",
        "warn_no_route_title": "Nessuna Rotta",
        "warn_no_route_msg": "Scarica prima il piano da SimBrief o carica un file .PLN!",
        "warn_pln_coords_title": "Coordinate Mancanti nel file .PLN",
        "warn_pln_coords_msg": (
            "Questo file .pln (formato MSFS 2024) contiene solo i nomi dei waypoint senza coordinate geografiche.\n\n"
            "Assicurati che il tuo SimBrief ID sia inserito correttamente o esporta il file in formato 'FS2020 (.pln)' da SimBrief / Little Navmap."
        ),
        "err_pln_title": "Errore Caricamento PLN",
        "err_pln_msg": "Impossibile leggere il file .pln:\n",
        "err_sb_title": "Errore SimBrief",
        "err_sb_http": "Errore HTTP: ",
        "err_sb_msg": "Impossibile scaricare il piano da SimBrief:\n",
        "err_sc_title": "Errore SimConnect",
        "err_sc_msg": "Assicurati che MSFS sia aperto.\nDettaglio: "
    },
    "EN": {
        "lang_btn": " IT",
        "discord_btn": "DISCORD",
        "fetch_ofp": "Fetch OFP",
        "load_pln": "Load .PLN",
        "connect_msfs": "Connect MSFS",
        "reconnect_msfs": "Reconnect MSFS",
        "status_disc": "● Status: Disconnected from MSFS",
        "status_conn": "● Status: Connected to MSFS (SimConnect Active)",
        "status_err": "● Status: MSFS Connection Error",
        "status_loading": "● Status: Fetching flight plan data...",
        "col_wp": "Waypoint",
        "col_lat": "Latitude",
        "col_lon": "Longitude",
        "col_dist": "Distance (NM)",
        "col_dep": "DEP",
        "col_dest": "DEST",
        "col_ete": "ETE (DEST)",
        "col_efob": "EFOB (KG)",
        "col_xtk": "XTK (NM)",
        "prev_wp": "<< Prev WP",
        "next_wp": "Next WP >>",
        "start_nav": "START NAV (HDG)",
        "stop_nav": "NAV ACTIVE (STOP)",
        "route_done": "ROUTE COMPLETED",
        "exit": "EXIT",
        "howto_title": "HOW TO - MB-339 Cockpit Setup & Guide",
        "howto_header": "OPERATING GUIDE & COCKPIT SETUP",
        "howto_close": "CLOSE GUIDE",
        "howto_text": (
            "1. LOADING FLIGHT PLAN (SIMBRIEF OR .PLN FILE):\n"
            "   • From SimBrief: enter your Pilot ID and click 'Fetch OFP'.\n"
            "   • From Local File: click 'Load .PLN' and select a .pln file\n"
            "     generated by MSFS 2024 / 2020, Little Navmap, or SimBrief.\n"
            "   • Click 'Connect MSFS' to activate the SimConnect bridge.\n\n"
            "2. MB-339 COCKPIT SETUP:\n"
            "   • Turn on the aircraft electrical power and avionics.\n"
            "   • Locate the Flight Director / Autopilot panel on the glareshield.\n"
            "   • Ensure the Autopilot is engaged (Master ON).\n"
            "   • Press the HDG (Heading) button to enable heading bug tracking.\n"
            "   • To hold altitude, engage ALT HOLD once at cruise altitude.\n\n"
            "3. AUTOMATIC NAVIGATION:\n"
            "   • Click 'START NAV (HDG)' in the application.\n"
            "   • The utility calculates real-time Bearing and automatically\n"
            "     updates the Heading Bug on your aircraft HSI.\n"
            "   • Upon reaching a waypoint (within 0.8 NM), the app automatically\n"
            "     sequences to the next waypoint until destination.\n\n"
            "4. MANUAL ROUTE SEQUENCING:\n"
            "   • Use the '<< Prev WP' and 'Next WP >>' buttons exclusively\n"
            "     to manually switch the active waypoint at any time."
        ),
        "dlg_open_pln": "Select MSFS Flight Plan (.pln)",
        "dlg_all_files": "All files",
        "warn_title": "Warning",
        "warn_sb_id": "Please enter your SimBrief Pilot ID.",
        "warn_not_conn_title": "Not Connected",
        "warn_not_conn_msg": "Please connect to MSFS first!",
        "warn_no_route_title": "No Flight Plan",
        "warn_no_route_msg": "Please fetch a SimBrief OFP or load a .PLN file first!",
        "warn_pln_coords_title": "Missing Coordinates in .PLN file",
        "warn_pln_coords_msg": (
            "This .pln file (MSFS 2024 format) only contains waypoint identifiers without geographic coordinates.\n\n"
            "Make sure your SimBrief ID is entered correctly or export the file in 'FS2020 (.pln)' format from SimBrief / Little Navmap."
        ),
        "err_pln_title": "PLN Load Error",
        "err_pln_msg": "Unable to read the .pln file:\n",
        "err_sb_title": "SimBrief Error",
        "err_sb_http": "HTTP Error: ",
        "err_sb_msg": "Unable to fetch flight plan from SimBrief:\n",
        "err_sc_title": "SimConnect Error",
        "err_sc_msg": "Make sure MSFS is running.\nDetail: "
    }
}


class MB339NavApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MB-339 SimBrief & PLN GPS Nav System v2.3")
        self.root.geometry("1040x720") 
        self.root.configure(bg="#121417")
        self.root.resizable(False, False)

        # Intercetta la chiusura della finestra dalla "X" in alto a destra
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

        # Lock di sincronizzazione per il multi-threading
        self.data_lock = threading.Lock()

        # Imposta e genera l'icona GPS e le icone delle bandiere
        self.setup_gps_icon()
        self.create_flag_icons()

        # Variabili di stato e lingua (Avvio predefinito in Inglese "EN")
        self.lang = "EN"
        self.conn_state = "disc"
        self.route_completed = False
        
        # Gestione configurazione ID SimBrief salvato localmente
        self.config_file = "mb339_nav_config.json"
        saved_id = self.load_saved_simbrief_id()
        self.simbrief_user = tk.StringVar(value=saved_id)

        self.mask_timer = None
        self.waypoints = []
        self.current_wp_index = 0
        self.nav_active = False
        self.connected = False
        self.route_synced = False
        self.howto_win = None
        self.howto_header_lbl = None
        self.howto_txt_box = None
        self.howto_btn_close = None
        
        # Dati rotta
        self.plane_lat = None
        self.plane_lon = None
        self.origin_icao = "---"
        self.dest_icao = "---"

        # Oggetti SimConnect
        self.sm = None
        self.aq = None
        self.ae = None
        self.ev_hdg_set = None
        self.ev_ap_master = None
        self.ev_hdg_hold = None

        self.setup_ui()

        # Avvia il timer iniziale di 3 secondi per mascherare l'ID se già presente
        if saved_id:
            self.schedule_id_mask()

        # Avvia il thread di aggiornamento in background
        self.running = True
        self.worker_thread = threading.Thread(target=self.sim_loop, daemon=True)
        self.worker_thread.start()

    def load_saved_simbrief_id(self):
        """Legge l'ID SimBrief salvato nel file di configurazione locale."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("simbrief_id", "")
        except Exception:
            pass
        return ""

    def save_simbrief_id(self, user_id):
        """Salva l'ID SimBrief nel file di configurazione locale."""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump({"simbrief_id": user_id}, f)
        except Exception:
            pass

    def create_flag_icons(self):
        """Disegna le bandiere Italiana (IT) e Britannica (GB) in pixel-art per il pulsante lingua."""
        self.flag_it = tk.PhotoImage(width=18, height=12)
        for y in range(12):
            for x in range(18):
                if x < 6:
                    color = "#009246"
                elif x < 12:
                    color = "#ffffff"
                else:
                    color = "#ce2b37"
                self.flag_it.put(color, (x, y))

        self.flag_gb = tk.PhotoImage(width=18, height=12)
        for y in range(12):
            for x in range(18):
                color = "#012169"
                diag1 = abs(x - (y * 1.5))
                diag2 = abs(x - ((11 - y) * 1.5))
                if diag1 < 2.2 or diag2 < 2.2:
                    color = "#ffffff"
                if diag1 < 1.0 or diag2 < 1.0:
                    color = "#c8102e"
                if 7 <= x <= 10 or 4 <= y <= 7:
                    color = "#ffffff"
                if 8 <= x <= 9 or 5 <= y <= 6:
                    color = "#c8102e"
                self.flag_gb.put(color, (x, y))

    def get_target_flag(self):
        return self.flag_gb if self.lang == "IT" else self.flag_it

    def t(self, key):
        return TRANSLATIONS[self.lang].get(key, key)

    def toggle_language(self):
        self.lang = "EN" if self.lang == "IT" else "IT"
        self.apply_language()

    def apply_language(self):
        self.btn_lang.config(text=self.t("lang_btn"), image=self.get_target_flag())
        self.btn_discord.config(text=self.t("discord_btn"))
        self.btn_sb.config(text=self.t("fetch_ofp"))
        self.btn_pln.config(text=self.t("load_pln"))

        if self.conn_state == "conn":
            self.btn_conn.config(text=self.t("reconnect_msfs"))
            self.lbl_status.config(text=self.t("status_conn"), fg="#4ec9b0")
        elif self.conn_state == "err":
            self.btn_conn.config(text=self.t("connect_msfs"))
            self.lbl_status.config(text=self.t("status_err"), fg="#ff5555")
        else:
            self.btn_conn.config(text=self.t("connect_msfs"))
            self.lbl_status.config(text=self.t("status_disc"), fg="#ff5555")

        self.lbl_dep_title.config(text=self.t("col_dep"))
        self.lbl_dest_title.config(text=self.t("col_dest"))
        self.lbl_ete_title.config(text=self.t("col_ete"))
        self.lbl_efob_title.config(text=self.t("col_efob"))
        self.lbl_xtk_title.config(text=self.t("col_xtk"))

        self.tree.heading("ident", text=self.t("col_wp"))
        self.tree.heading("lat", text=self.t("col_lat"))
        self.tree.heading("lon", text=self.t("col_lon"))
        self.tree.heading("dist", text=self.t("col_dist"))

        self.btn_prev.config(text=self.t("prev_wp"))
        self.btn_next.config(text=self.t("next_wp"))
        self.btn_exit.config(text=self.t("exit"))

        if self.nav_active:
            self.btn_nav.config(text=self.t("stop_nav"), bg="#4ec9b0", fg="#121417")
        elif self.route_completed:
            self.btn_nav.config(text=self.t("route_done"), bg="#4ec9b0", fg="#121417")
        else:
            self.btn_nav.config(text=self.t("start_nav"), bg="#ffb000", fg="#121417")

        if self.howto_win is not None and tk.Toplevel.winfo_exists(self.howto_win):
            self.howto_win.title(self.t("howto_title"))
            self.howto_header_lbl.config(text=self.t("howto_header"))
            self.howto_btn_close.config(text=self.t("howto_close"))
            self.howto_txt_box.config(state="normal")
            self.howto_txt_box.delete("1.0", "end")
            self.howto_txt_box.insert("1.0", self.t("howto_text"))
            self.howto_txt_box.config(state="disabled")

    def open_discord(self):
        """Apre il link del server Discord SKYSIM PILOT nel browser predefinito."""
        webbrowser.open("https://discord.gg/YYJEnge3SS")

    def setup_gps_icon(self):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        ico_path = os.path.join(base_path, "gps_icon.ico")

        if os.path.exists(ico_path):
            try:
                self.root.iconbitmap(ico_path)
            except Exception:
                pass

        icon = tk.PhotoImage(width=32, height=32)
        cx, cy = 15.5, 15.5
        for y in range(32):
            for x in range(32):
                dist = math.hypot(x - cx, y - cy)
                if 12.0 <= dist <= 14.2:
                    icon.put("#00ff66", (x, y))
                elif dist < 12.0:
                    icon.put("#141414", (x, y))
                if dist < 12.0 and (abs(x - 16) <= 1 or abs(y - 16) <= 1):
                    if dist > 4.0:
                        icon.put("#00aa44", (x, y))
                if dist <= 3.0:
                    icon.put("#ff3333" if y < 16 else "#00ff66", (x, y))

        self.app_icon = icon
        self.root.iconphoto(True, self.app_icon)

        local_ico = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gps_icon.ico")
        if not os.path.exists(local_ico):
            try:
                from PIL import Image, ImageDraw
                img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
                draw = ImageDraw.Draw(img)
                draw.ellipse((4, 4, 60, 60), fill=(20, 20, 20, 255), outline=(0, 255, 102, 255), width=4)
                draw.line((32, 8, 32, 56), fill=(0, 180, 80, 255), width=2)
                draw.line((8, 32, 56, 32), fill=(0, 180, 80, 255), width=2)
                draw.polygon([(32, 12), (24, 36), (32, 30), (40, 36)], fill=(0, 255, 102, 255))
                draw.ellipse((28, 28, 36, 36), fill=(255, 60, 60, 255))
                img.save(local_ico, format="ICO", sizes=[(64, 64), (32, 32), (16, 16)])
            except Exception:
                pass

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure("Dark.Treeview", 
                        background="#1a1d24", 
                        foreground="#e0e0e0", 
                        fieldbackground="#1a1d24", 
                        borderwidth=0, 
                        font=("Consolas", 10))
        style.configure("Dark.Treeview.Heading", 
                        background="#262b36", 
                        foreground="#ffb000", 
                        font=("Segoe UI", 9, "bold"))
        style.map("Dark.Treeview", background=[('selected', '#333b4d')])

        # --- TOP BAR ---
        top_bar = tk.Frame(self.root, bg="#121417", padx=15, pady=10)
        top_bar.pack(fill="x")

        tk.Label(top_bar, text="✈  MB339-NAV-FS", fg="#ffb000", bg="#121417", font=("Segoe UI", 12, "bold")).pack(side="left")
        
        self.btn_howto = tk.Button(top_bar, text="HOW TO", command=self.toggle_howto, bg="#646695", fg="#ffffff", activebackground="#787ab0", activeforeground="#ffffff", font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=2)
        self.btn_howto.pack(side="right", padx=4)

        self.btn_discord = tk.Button(top_bar, text=self.t("discord_btn"), command=self.open_discord, bg="#5865F2", fg="#ffffff", activebackground="#4752C4", activeforeground="#ffffff", font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=2)
        self.btn_discord.pack(side="right", padx=4)

        self.btn_lang = tk.Button(
            top_bar,
            text=self.t("lang_btn"),
            image=self.get_target_flag(),
            compound="left",
            command=self.toggle_language,
            bg="#262b36",
            fg="#ffffff",
            activebackground="#333b4d",
            activeforeground="#ffffff",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=8,
            pady=2
        )
        self.btn_lang.pack(side="right", padx=4)

        # --- FRAME 1: Configurazione ---
        cfg_frame = tk.Frame(self.root, bg="#1a1d24", bd=0, padx=12, pady=12)
        cfg_frame.pack(fill="x", padx=15, pady=5)

        tk.Label(cfg_frame, text="SIMBRIEF ID:", fg="#8a92a2", bg="#1a1d24", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, padx=4, pady=5, sticky="w")

        self.entry_sb = tk.Entry(
            cfg_frame,
            textvariable=self.simbrief_user,
            width=9,
            font=("Consolas", 11),
            bg="#121417",
            fg="#ffb000",
            insertbackground="white",
            relief="flat"
        )
        self.entry_sb.grid(row=0, column=1, padx=4, pady=5, ipady=3)

        self.entry_sb.bind("<KeyRelease>", self.on_id_activity)
        self.entry_sb.bind("<FocusIn>", self.on_id_activity)

        self.btn_sb = tk.Button(cfg_frame, text=self.t("fetch_ofp"), command=self.start_load_simbrief_thread, bg="#0066cc", fg="white", activebackground="#0055aa", activeforeground="white", font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=4)
        self.btn_sb.grid(row=0, column=2, padx=5, pady=5)

        self.btn_pln = tk.Button(cfg_frame, text=self.t("load_pln"), command=self.start_load_pln_thread, bg="#d97706", fg="white", activebackground="#b45309", activeforeground="white", font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=4)
        self.btn_pln.grid(row=0, column=3, padx=5, pady=5)

        self.btn_conn = tk.Button(cfg_frame, text=self.t("connect_msfs"), command=self.connect_msfs, bg="#2d6a2e", fg="white", activebackground="#235423", activeforeground="white", font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=4)
        self.btn_conn.grid(row=0, column=4, padx=5, pady=5)

        self.lbl_status = tk.Label(cfg_frame, text=self.t("status_disc"), fg="#ff5555", bg="#1a1d24", font=("Segoe UI", 9))
        self.lbl_status.grid(row=1, column=0, columnspan=5, pady=(8, 0), sticky="w")

        # --- FRAME 2: Display Digitale Stile Radio/GPS (ESPANSIVO A TUTTA LARGHEZZA) ---
        nav_frame = tk.Frame(self.root, bg="#0b0c0e", bd=1, relief="solid", highlightbackground="#262b36", highlightthickness=1, padx=12, pady=12)
        nav_frame.pack(fill="x", padx=15, pady=8)

        for i in range(8):
            nav_frame.grid_columnconfigure(i, weight=1)

        tk.Label(nav_frame, text="ACTIVE WAYPOINT", fg="#636e7b", bg="#0b0c0e", font=("Consolas", 11, "bold")).grid(row=0, column=0)
        tk.Label(nav_frame, text="BEARING (HDG)", fg="#636e7b", bg="#0b0c0e", font=("Consolas", 11, "bold")).grid(row=0, column=1)
        tk.Label(nav_frame, text="DISTANCE (NM)", fg="#636e7b", bg="#0b0c0e", font=("Consolas", 11, "bold")).grid(row=0, column=2)
        self.lbl_dep_title = tk.Label(nav_frame, text=self.t("col_dep"), fg="#636e7b", bg="#0b0c0e", font=("Consolas", 11, "bold"))
        self.lbl_dep_title.grid(row=0, column=3)
        self.lbl_dest_title = tk.Label(nav_frame, text=self.t("col_dest"), fg="#636e7b", bg="#0b0c0e", font=("Consolas", 11, "bold"))
        self.lbl_dest_title.grid(row=0, column=4)
        self.lbl_ete_title = tk.Label(nav_frame, text=self.t("col_ete"), fg="#636e7b", bg="#0b0c0e", font=("Consolas", 11, "bold"))
        self.lbl_ete_title.grid(row=0, column=5)
        self.lbl_efob_title = tk.Label(nav_frame, text=self.t("col_efob"), fg="#636e7b", bg="#0b0c0e", font=("Consolas", 11, "bold"))
        self.lbl_efob_title.grid(row=0, column=6)
        self.lbl_xtk_title = tk.Label(nav_frame, text=self.t("col_xtk"), fg="#636e7b", bg="#0b0c0e", font=("Consolas", 11, "bold"))
        self.lbl_xtk_title.grid(row=0, column=7)

        self.lbl_wp_name = tk.Label(nav_frame, text="---", fg="#ffb000", bg="#0b0c0e", font=("Consolas", 26, "bold"))
        self.lbl_wp_name.grid(row=1, column=0, pady=(2, 0))

        self.lbl_brg = tk.Label(nav_frame, text="---°", fg="#ffb000", bg="#0b0c0e", font=("Consolas", 26, "bold"))
        self.lbl_brg.grid(row=1, column=1, pady=(2, 0))

        self.lbl_dist = tk.Label(nav_frame, text="--.-", fg="#ffb000", bg="#0b0c0e", font=("Consolas", 26, "bold"))
        self.lbl_dist.grid(row=1, column=2, pady=(2, 0))

        self.lbl_dep = tk.Label(nav_frame, text="---", fg="#ffb000", bg="#0b0c0e", font=("Consolas", 26, "bold"))
        self.lbl_dep.grid(row=1, column=3, pady=(2, 0))

        self.lbl_dest = tk.Label(nav_frame, text="---", fg="#ffb000", bg="#0b0c0e", font=("Consolas", 26, "bold"))
        self.lbl_dest.grid(row=1, column=4, pady=(2, 0))

        self.lbl_ete = tk.Label(nav_frame, text="--:--", fg="#4ec9b0", bg="#0b0c0e", font=("Consolas", 26, "bold"))
        self.lbl_ete.grid(row=1, column=5, pady=(2, 0))

        self.lbl_efob = tk.Label(nav_frame, text="---", fg="#4ec9b0", bg="#0b0c0e", font=("Consolas", 26, "bold"))
        self.lbl_efob.grid(row=1, column=6, pady=(2, 0))

        self.lbl_xtk = tk.Label(nav_frame, text="---", fg="#4ec9b0", bg="#0b0c0e", font=("Consolas", 26, "bold"))
        self.lbl_xtk.grid(row=1, column=7, pady=(2, 0))

        sep = tk.Frame(nav_frame, bg="#1a1d24", height=1)
        sep.grid(row=2, column=0, columnspan=8, sticky="ew", pady=(8, 6))

        self.lbl_pos = tk.Label(nav_frame, text="GPS POS: LAT --.----  |  LON --.----", fg="#3399ff", bg="#0b0c0e", font=("Consolas", 9, "bold"))
        self.lbl_pos.grid(row=3, column=0, columnspan=8, sticky="w")

        # --- FRAME 3: Tabella Waypoint Rotta ---
        list_frame = tk.Frame(self.root, bg="#121417")
        list_frame.pack(fill="both", expand=True, padx=15, pady=5)

        columns = ("idx", "ident", "lat", "lon", "dist")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=11, selectmode="browse", style="Dark.Treeview")
        self.tree.heading("idx", text="#")
        self.tree.heading("ident", text=self.t("col_wp"))
        self.tree.heading("lat", text=self.t("col_lat"))
        self.tree.heading("lon", text=self.t("col_lon"))
        self.tree.heading("dist", text=self.t("col_dist"))

        self.tree.column("idx", width=45, anchor="center")
        self.tree.column("ident", width=180, anchor="center")
        self.tree.column("lat", width=210, anchor="center")
        self.tree.column("lon", width=210, anchor="center")
        self.tree.column("dist", width=210, anchor="center")

        self.tree.bind("<Button-1>", lambda e: "break")
        self.tree.bind("<ButtonRelease-1>", lambda e: "break")
        self.tree.bind("<B1-Motion>", lambda e: "break")
        self.tree.bind("<Double-1>", lambda e: "break")
        self.tree.bind("<Key>", lambda e: "break")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- FRAME 4: Controlli ---
        ctrl_frame = tk.Frame(self.root, bg="#1a1d24", bd=0, padx=12, pady=12)
        ctrl_frame.pack(fill="x", padx=15, pady=10)

        self.btn_prev = tk.Button(ctrl_frame, text=self.t("prev_wp"), command=self.prev_wp, bg="#262b36", fg="#e0e0e0", activebackground="#333b4d", activeforeground="white", font=("Segoe UI", 9, "bold"), width=12, relief="flat", pady=6)
        self.btn_prev.pack(side="left", padx=4)

        self.btn_nav = tk.Button(ctrl_frame, text=self.t("start_nav"), command=self.toggle_nav, bg="#ffb000", fg="#121417", activebackground="#ffc833", activeforeground="#121417", font=("Segoe UI", 10, "bold"), width=20, relief="flat", pady=6)
        self.btn_nav.pack(side="left", expand=True, padx=4)

        self.btn_next = tk.Button(ctrl_frame, text=self.t("next_wp"), command=self.next_wp, bg="#262b36", fg="#e0e0e0", activebackground="#333b4d", activeforeground="white", font=("Segoe UI", 9, "bold"), width=12, relief="flat", pady=6)
        self.btn_next.pack(side="left", padx=4)

        self.btn_exit = tk.Button(ctrl_frame, text=self.t("exit"), command=self.quit_app, bg="#a83232", fg="white", activebackground="#c53f3f", activeforeground="white", font=("Segoe UI", 9, "bold"), width=9, relief="flat", pady=6)
        self.btn_exit.pack(side="right", padx=4)

    def toggle_howto(self):
        if self.howto_win is not None and tk.Toplevel.winfo_exists(self.howto_win):
            self.howto_win.destroy()
            self.howto_win = None
        else:
            self.howto_win = tk.Toplevel(self.root)
            self.howto_win.title(self.t("howto_title"))
            
            x = self.root.winfo_rootx()
            y = self.root.winfo_rooty()
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            
            self.howto_win.geometry(f"680x{height}+{x + width + 10}+{y}")
            self.howto_win.configure(bg="#121417")
            self.howto_win.resizable(False, False)
            
            self.howto_win.protocol("WM_DELETE_WINDOW", self.close_howto)

            self.howto_header_lbl = tk.Label(
                self.howto_win, 
                text=self.t("howto_header"), 
                fg="#ffb000", 
                bg="#121417", 
                font=("Segoe UI", 13, "bold")
            )
            self.howto_header_lbl.pack(pady=(15, 8), padx=20, anchor="w")

            self.howto_txt_box = tk.Text(
                self.howto_win, 
                wrap="word", 
                bg="#0b0c0e", 
                fg="#e0e0e0", 
                font=("Consolas", 11),
                height=26,
                padx=15, 
                pady=12, 
                bd=0, 
                highlightthickness=1,
                highlightbackground="#262b36"
            )
            self.howto_txt_box.insert("1.0", self.t("howto_text"))
            self.howto_txt_box.config(state="disabled")
            self.howto_txt_box.pack(fill="x", padx=20, pady=6)

            self.howto_btn_close = tk.Button(
                self.howto_win, 
                text=self.t("howto_close"), 
                command=self.close_howto, 
                bg="#a83232", 
                fg="white", 
                font=("Segoe UI", 10, "bold"), 
                relief="flat", 
                padx=20, 
                pady=8
            )
            self.howto_btn_close.pack(pady=(8, 15))

    def close_howto(self):
        if self.howto_win is not None:
            try:
                self.howto_win.destroy()
            except Exception:
                pass
            self.howto_win = None

    def on_id_activity(self, event=None):
        self.entry_sb.config(show="")
        self.schedule_id_mask()

    def schedule_id_mask(self):
        if self.mask_timer is not None:
            self.root.after_cancel(self.mask_timer)
        self.mask_timer = self.root.after(3000, self.mask_simbrief_id)

    def mask_simbrief_id(self):
        user_val = self.simbrief_user.get().strip()
        if user_val:
            self.entry_sb.config(show="*")
            self.save_simbrief_id(user_val)

    def quit_app(self):
        with self.data_lock:
            self.nav_active = False
            self.running = False
        self.close_howto()
        try:
            if self.sm:
                self.sm.exit()
        except Exception:
            pass
        self.root.destroy()
        sys.exit(0)

    @staticmethod
    def parse_world_position(pos_str):
        parts = [p.strip() for p in pos_str.split(",")]
        if len(parts) < 2:
            return None, None

        def dms_to_dd(dms_str):
            dms_str = dms_str.strip()
            try:
                return float(dms_str)
            except ValueError:
                pass

            match = re.search(r"([NSWE])\s*(\d+)\D+(\d+)\D+([\d.]+)", dms_str, re.IGNORECASE)
            if match:
                direction = match.group(1).upper()
                deg = float(match.group(2))
                minutes = float(match.group(3))
                seconds = float(match.group(4))
                dd = deg + (minutes / 60.0) + (seconds / 3600.0)
                if direction in ("S", "W"):
                    dd = -dd
                return dd
            return None

        lat = dms_to_dd(parts[0])
        lon = dms_to_dd(parts[1])
        return lat, lon

    @staticmethod
    def calculate_xtk_nm(lat1, lon1, lat2, lon2, plane_lat, plane_lon):
        brg_leg = MB339NavApp.calculate_bearing(lat1, lon1, lat2, lon2)
        brg_plane = MB339NavApp.calculate_bearing(lat1, lon1, plane_lat, plane_lon)
        dist_plane = MB339NavApp.calculate_distance_nm(lat1, lon1, plane_lat, plane_lon)
        
        diff = math.radians(brg_plane - brg_leg)
        xtk = math.asin(math.sin(dist_plane / 3440.065) * math.sin(diff)) * 3440.065
        return xtk

    def fetch_simbrief_coords_map(self):
        coords_map = {}
        user = self.simbrief_user.get().strip()
        if not user:
            return coords_map

        try:
            url = f"https://www.simbrief.com/api/xml.fetcher.php?userid={user}"
            resp = requests.get(url, timeout=6)
            if resp.status_code == 200:
                sb_root = ET.fromstring(resp.content)
                for section in [".//origin", ".//destination"]:
                    node = sb_root.find(section)
                    if node is not None:
                        icao = node.find("icao_code")
                        lat = node.find("pos_lat") if node.find("pos_lat") is not None else node.find("lat")
                        lon = node.find("pos_long") if node.find("pos_long") is not None else node.find("lon")
                        if icao is not None and lat is not None and lon is not None:
                            coords_map[icao.text.strip().upper()] = (float(lat.text), float(lon.text))

                for fix in sb_root.findall(".//navlog/fix"):
                    ident = fix.find("ident")
                    lat = fix.find("pos_lat")
                    lon = fix.find("pos_long")
                    if ident is not None and lat is not None and lon is not None:
                        try:
                            coords_map[ident.text.strip().upper()] = (float(lat.text), float(lon.text))
                        except ValueError:
                            pass
        except Exception:
            pass

        return coords_map

    def start_load_pln_thread(self):
        user = self.simbrief_user.get().strip()
        if user:
            self.save_simbrief_id(user)

        file_path = filedialog.askopenfilename(
            title=self.t("dlg_open_pln"),
            filetypes=[("MSFS Flight Plan", "*.pln"), (self.t("dlg_all_files"), "*.*")]
        )
        if file_path:
            self.lbl_status.config(text=self.t("status_loading"), fg="#ffb000")
            threading.Thread(target=self.load_pln_file, args=(file_path,), daemon=True).start()

    def load_pln_file(self, file_path):
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            wps = []

            has_world_pos = root.find(".//WorldPosition") is not None
            sb_coords = {} if has_world_pos else self.fetch_simbrief_coords_map()

            dep_node = root.find(".//DepartureID")
            origin_icao = dep_node.text.strip().upper() if dep_node is not None and dep_node.text else ""
            if origin_icao and origin_icao in sb_coords:
                lat, lon = sb_coords[origin_icao]
                wps.append({"name": origin_icao, "lat": lat, "lon": lon})

            for wp_elem in root.findall(".//ATCWaypoint"):
                ident = wp_elem.get("id")
                if not ident:
                    id_node = wp_elem.find("ATCWaypointID")
                    if id_node is not None and id_node.text:
                        ident = id_node.text.strip()
                if not ident:
                    icao_node = wp_elem.find(".//ICAOIdent")
                    if icao_node is not None and icao_node.text:
                        ident = icao_node.text.strip()
                ident = ident.strip() if ident else "WPT"

                lat, lon = None, None

                wp_pos = wp_elem.find("WorldPosition")
                if wp_pos is not None and wp_pos.text:
                    lat, lon = self.parse_world_position(wp_pos.text)

                if lat is None or lon is None:
                    lat_node = wp_elem.find(".//Latitude")
                    lon_node = wp_elem.find(".//Longitude")
                    if lat_node is not None and lon_node is not None and lat_node.text and lon_node.text:
                        try:
                            lat = float(lat_node.text.strip())
                            lon = float(lon_node.text.strip())
                        except ValueError:
                            pass

                if (lat is None or lon is None) and ident.upper() in sb_coords:
                    lat, lon = sb_coords[ident.upper()]

                if lat is not None and lon is not None and (lat != 0.0 or lon != 0.0):
                    if not wps or wps[-1]["name"] != ident:
                        wps.append({"name": ident, "lat": lat, "lon": lon})

            dest_node = root.find(".//DestinationID")
            dest_icao = dest_node.text.strip().upper() if dest_node is not None and dest_node.text else ""
            if dest_icao and dest_icao in sb_coords:
                lat, lon = sb_coords[dest_icao]
                if not wps or wps[-1]["name"] != dest_icao:
                    wps.append({"name": dest_icao, "lat": lat, "lon": lon})

            if not wps:
                self.root.after(0, lambda: messagebox.showwarning(self.t("warn_pln_coords_title"), self.t("warn_pln_coords_msg")))
                self.root.after(0, self.update_status_after_action)
                return

            with self.data_lock:
                self.origin_icao = origin_icao if origin_icao else (wps[0]["name"] if wps else "---")
                self.dest_icao = dest_icao if dest_icao else (wps[-1]["name"] if wps else "---")
                self.route_completed = False
                self.waypoints = wps
                self.current_wp_index = 1 if len(wps) > 1 else 0
                self.route_synced = False 

            self.root.after(0, self.finalize_route_load)

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(self.t("err_pln_title"), f"{self.t('err_pln_msg')}{e}"))
            self.root.after(0, self.update_status_after_action)

    def start_load_simbrief_thread(self):
        user = self.simbrief_user.get().strip()
        if not user:
            messagebox.showwarning(self.t("warn_title"), self.t("warn_sb_id"))
            return

        self.save_simbrief_id(user)
        self.schedule_id_mask()
        self.lbl_status.config(text=self.t("status_loading"), fg="#ffb000")
        threading.Thread(target=self.load_simbrief, daemon=True).start()

    def load_simbrief(self):
        user = self.simbrief_user.get().strip()
        url = f"https://www.simbrief.com/api/xml.fetcher.php?userid={user}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                wps = []

                origin_icao = ""
                orig = root.find(".//origin")
                if orig is not None:
                    icao = orig.find("icao_code")
                    lat = orig.find("pos_lat") if orig.find("pos_lat") is not None else orig.find("lat")
                    lon = orig.find("pos_long") if orig.find("pos_long") is not None else orig.find("lon")
                    if icao is not None and lat is not None and lon is not None:
                        origin_icao = icao.text.strip()
                        wps.append({"name": icao.text, "lat": float(lat.text), "lon": float(lon.text)})

                for fix in root.findall(".//navlog/fix"):
                    ident = fix.find("ident")
                    lat = fix.find("pos_lat")
                    lon = fix.find("pos_long")
                    if ident is not None and lat is not None and lon is not None:
                        try:
                            lat_v, lon_v = float(lat.text), float(lon.text)
                            if lat_v != 0.0 and lon_v != 0.0:
                                if not wps or wps[-1]["name"] != ident.text:
                                    wps.append({"name": ident.text, "lat": lat_v, "lon": lon_v})
                        except ValueError:
                            continue

                dest_icao = ""
                dest = root.find(".//destination")
                if dest is not None:
                    icao = dest.find("icao_code")
                    lat = dest.find("pos_lat") if dest.find("pos_lat") is not None else dest.find("lat")
                    lon = dest.find("pos_long") if dest.find("pos_long") is not None else dest.find("lon")
                    if icao is not None and lat is not None and lon is not None:
                        dest_icao = icao.text.strip()
                        if not wps or wps[-1]["name"] != icao.text:
                            wps.append({"name": icao.text, "lat": float(lat.text), "lon": float(lon.text)})

                with self.data_lock:
                    self.origin_icao = origin_icao if origin_icao else "---"
                    self.dest_icao = dest_icao if dest_icao else "---"
                    self.route_completed = False
                    self.waypoints = wps
                    self.current_wp_index = 1 if len(wps) > 1 else 0
                    self.route_synced = False 

                self.root.after(0, self.finalize_route_load)
            else:
                self.root.after(0, lambda: messagebox.showerror(self.t("err_sb_title"), f"{self.t('err_sb_http')}{response.status_code}"))
                self.root.after(0, self.update_status_after_action)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(self.t("err_sb_title"), f"{self.t('err_sb_msg')}{e}"))
            self.root.after(0, self.update_status_after_action)

    def finalize_route_load(self):
        with self.data_lock:
            self.lbl_dep.config(text=self.origin_icao)
            self.lbl_dest.config(text=self.dest_icao)
            self.refresh_tree()

            if self.waypoints and self.current_wp_index < len(self.waypoints):
                active_wp = self.waypoints[self.current_wp_index]
                if self.plane_lat is not None and self.plane_lon is not None:
                    brg = self.calculate_bearing(self.plane_lat, self.plane_lon, active_wp["lat"], active_wp["lon"])
                    dist_nm = self.calculate_distance_nm(self.plane_lat, self.plane_lon, active_wp["lat"], active_wp["lon"])
                    self.update_telemetry_ui(active_wp["name"], brg, dist_nm, "--:--", "---", "---", "#4ec9b0")
                else:
                    self.lbl_wp_name.config(text=active_wp["name"])
                    self.lbl_brg.config(text="---°")
                    self.lbl_dist.config(text="--.-")
                    self.lbl_ete.config(text="--:--")
                    self.lbl_efob.config(text="---")
                    self.lbl_xtk.config(text="---", fg="#4ec9b0")
        self.update_status_after_action()

    def update_status_after_action(self):
        if self.connected:
            self.lbl_status.config(text=self.t("status_conn"), fg="#4ec9b0")
        else:
            self.lbl_status.config(text=self.t("status_disc"), fg="#ff5555")

    def refresh_tree(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for i, wp in enumerate(self.waypoints):
            prefix = "▶ " if i == self.current_wp_index else ""
            
            dist_str = "--.-"
            if self.plane_lat is not None and self.plane_lon is not None:
                d = self.calculate_distance_nm(self.plane_lat, self.plane_lon, wp["lat"], wp["lon"])
                dist_str = f"{d:.1f} NM"

            self.tree.insert("", "end", iid=str(i), values=(f"{prefix}{i+1}", wp["name"], f"{wp['lat']:.4f}", f"{wp['lon']:.4f}", dist_str))
        
        if self.waypoints and self.current_wp_index < len(self.waypoints):
            self.tree.selection_set(str(self.current_wp_index))
            self.tree.see(str(self.current_wp_index))

    def connect_msfs(self):
        try:
            self.sm = SimConnect()
            self.aq = AircraftRequests(self.sm, _time=200)
            self.ae = AircraftEvents(self.sm)

            self.ev_hdg_set = self.ae.find("HEADING_BUG_SET")
            self.ev_ap_master = self.ae.find("AP_MASTER")
            self.ev_hdg_hold = self.ae.find("AP_HDG_HOLD_ON")

            self.connected = True
            self.conn_state = "conn"
            self.lbl_status.config(text=self.t("status_conn"), fg="#4ec9b0")
            self.btn_conn.config(text=self.t("reconnect_msfs"), bg="#235423")
        except Exception as e:
            self.connected = False
            self.conn_state = "err"
            self.lbl_status.config(text=self.t("status_err"), fg="#ff5555")
            messagebox.showerror(self.t("err_sc_title"), f"{self.t('err_sc_msg')}{e}")

    def toggle_nav(self):
        if not self.connected:
            messagebox.showwarning(self.t("warn_not_conn_title"), self.t("warn_not_conn_msg"))
            return
        if not self.waypoints:
            messagebox.showwarning(self.t("warn_no_route_title"), self.t("warn_no_route_msg"))
            return

        with self.data_lock:
            self.route_completed = False
            self.nav_active = not self.nav_active
            is_active = self.nav_active

        if is_active:
            self.btn_nav.config(text=self.t("stop_nav"), bg="#4ec9b0", fg="#121417")
            try:
                if self.ev_hdg_hold:
                    self.ev_hdg_hold()
            except Exception:
                pass
        else:
            self.btn_nav.config(text=self.t("start_nav"), bg="#ffb000", fg="#121417")

    def prev_wp(self):
        with self.data_lock:
            if self.waypoints and self.current_wp_index > 0:
                self.current_wp_index -= 1
                self.refresh_tree()

    def next_wp(self):
        with self.data_lock:
            if self.waypoints and self.current_wp_index < len(self.waypoints) - 1:
                self.current_wp_index += 1
                self.refresh_tree()

    @staticmethod
    def calculate_bearing(lat1, lon1, lat2, lon2):
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dLon = lon2 - lon1
        x = math.sin(dLon) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dLon)
        return (math.degrees(math.atan2(x, y)) + 360) % 360

    @staticmethod
    def calculate_distance_nm(lat1, lon1, lat2, lon2):
        R_nm = 3440.065
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R_nm * c

    def sim_loop(self):
        update_counter = 0
        while True:
            with self.data_lock:
                if not self.running:
                    break
                is_connected = self.connected
                has_aq = self.aq is not None
                nav_act = self.nav_active
                wps = list(self.waypoints)
                wp_idx = self.current_wp_index

            if is_connected and has_aq:
                try:
                    p_lat = self.aq.get("PLANE_LATITUDE")
                    p_lon = self.aq.get("PLANE_LONGITUDE")

                    if p_lat is not None and p_lon is not None and p_lat != 0.0:
                        with self.data_lock:
                            self.plane_lat = p_lat
                            self.plane_lon = p_lon
                            
                            if wps and not self.route_synced:
                                if len(wps) > 1:
                                    best_idx = 1
                                    min_error = float('inf')
                                    for i in range(len(wps) - 1):
                                        wp1 = wps[i]
                                        wp2 = wps[i+1]
                                        d1 = self.calculate_distance_nm(wp1["lat"], wp1["lon"], p_lat, p_lon)
                                        d2 = self.calculate_distance_nm(p_lat, p_lon, wp2["lat"], wp2["lon"])
                                        leg = self.calculate_distance_nm(wp1["lat"], wp1["lon"], wp2["lat"], wp2["lon"])
                                        error = (d1 + d2) - leg
                                        if error < min_error:
                                            min_error = error
                                            best_idx = i + 1
                                    self.current_wp_index = best_idx
                                    wp_idx = best_idx 
                                self.route_synced = True
                                self.root.after(0, self.refresh_tree)

                        self.root.after(0, self.lbl_pos.config, {"text": f"GPS POS: LAT {p_lat:.4f}  |  LON {p_lon:.4f}"})

                        if wps and wp_idx < len(wps):
                            target = wps[wp_idx]
                            brg = self.calculate_bearing(p_lat, p_lon, target["lat"], target["lon"])
                            dist_nm = self.calculate_distance_nm(p_lat, p_lon, target["lat"], target["lon"])

                            # XTK Calculation
                            xtk_str = "---"
                            xtk_color = "#4ec9b0"
                            if wp_idx > 0:
                                prev_wp = wps[wp_idx - 1]
                                xtk_val = self.calculate_xtk_nm(prev_wp["lat"], prev_wp["lon"], target["lat"], target["lon"], p_lat, p_lon)
                                xtk_abs = abs(xtk_val)
                                dir_str = "R" if xtk_val > 0 else "L"
                                xtk_str = f"{dir_str} {xtk_abs:.1f}"
                                if xtk_abs > 2.0:
                                    xtk_color = "#ff5555"

                            total_dist_remaining = dist_nm
                            for i in range(wp_idx, len(wps) - 1):
                                total_dist_remaining += self.calculate_distance_nm(wps[i]["lat"], wps[i]["lon"], wps[i+1]["lat"], wps[i+1]["lon"])

                            ete_str = "--:--"
                            efob_str = "---"
                            
                            try:
                                gs = self.aq.get("GPS_GROUND_SPEED")
                                if gs is not None:
                                    gs = gs * 1.94384 
                                else:
                                    gs = self.aq.get("AIRSPEED_TRUE")

                                if gs is not None and gs > 30:
                                    time_hours = total_dist_remaining / gs
                                    h = int(time_hours)
                                    m = int((time_hours - h) * 60)
                                    ete_str = f"{h:02d}:{m:02d}"

                                    fob_gal = self.aq.get("FUEL_TOTAL_QUANTITY")
                                    
                                    ff_gph = self.aq.get("ENG_FUEL_FLOW_GPH:1")
                                    if ff_gph is None:
                                        ff_pph = self.aq.get("ENG_FUEL_FLOW_PPH:1")
                                        if ff_pph is not None:
                                            ff_gph = ff_pph / 6.7 

                                    if fob_gal is not None and ff_gph is not None:
                                        burn_gal = ff_gph * time_hours
                                        efob_gal = fob_gal - burn_gal
                                        if efob_gal < 0: 
                                            efob_gal = 0
                                        
                                        efob_kg = efob_gal * 3.03
                                        efob_str = f"{int(efob_kg)}"
                            except Exception:
                                pass

                            self.root.after(0, self.update_telemetry_ui, target["name"], brg, dist_nm, ete_str, efob_str, xtk_str, xtk_color)

                            update_counter += 1
                            if update_counter >= 3:
                                update_counter = 0
                                self.root.after(0, self.refresh_tree)

                            if nav_act:
                                if self.ev_hdg_set:
                                    try:
                                        self.ev_hdg_set(int(round(brg)))
                                    except Exception:
                                        pass

                                if dist_nm < 0.8:
                                    with self.data_lock:
                                        if self.current_wp_index < len(self.waypoints) - 1:
                                            self.current_wp_index += 1
                                            self.root.after(0, self.refresh_tree)
                                        else:
                                            self.nav_active = False
                                            self.route_completed = True
                                            self.root.after(0, self.btn_nav.config, {"text": self.t("route_done"), "bg": "#4ec9b0", "fg": "#121417"})
                except Exception:
                    with self.data_lock:
                        self.connected = False
                        self.conn_state = "disc"
                    self.root.after(0, lambda: self.lbl_status.config(text=self.t("status_disc"), fg="#ff5555"))
            
            time.sleep(1)

    def update_telemetry_ui(self, name, brg, dist_nm, ete_str, efob_str, xtk_str, xtk_color):
        self.lbl_wp_name.config(text=name)
        self.lbl_brg.config(text=f"{int(round(brg)):03d}°")
        self.lbl_dist.config(text=f"{dist_nm:.1f}")
        self.lbl_ete.config(text=ete_str)
        self.lbl_efob.config(text=efob_str)
        self.lbl_xtk.config(text=xtk_str, fg=xtk_color)


if __name__ == "__main__":
    root = tk.Tk()
    app = MB339NavApp(root)
    root.mainloop()