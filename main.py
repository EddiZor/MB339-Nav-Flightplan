import os
import sys
import re
import time
import math
import ctypes
import threading
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


class MB339NavApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MB-339 SimBrief & PLN GPS Nav System")
        self.root.geometry("740x720")
        self.root.configure(bg="#121417")  # Sfondo scuro stile dark app
        self.root.resizable(False, False)

        # Intercetta la chiusura della finestra dalla "X" in alto a destra
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

        # Imposta e genera l'icona GPS
        self.setup_gps_icon()

        # Variabili di stato
        self.simbrief_user = tk.StringVar(value="312844")
        self.mask_timer = None
        self.waypoints = []
        self.current_wp_index = 0
        self.nav_active = False
        self.connected = False
        self.howto_win = None
        
        # Coordinate attuali dell'aereo
        self.plane_lat = None
        self.plane_lon = None

        # Oggetti SimConnect
        self.sm = None
        self.aq = None
        self.ae = None
        self.ev_hdg_set = None
        self.ev_ap_master = None
        self.ev_hdg_hold = None

        self.setup_ui()

        # Avvia il timer iniziale di 3 secondi per mascherare il SimBrief ID predefinito
        self.schedule_id_mask()

        # Avvia il thread di aggiornamento in background
        self.running = True
        self.worker_thread = threading.Thread(target=self.sim_loop, daemon=True)
        self.worker_thread.start()

    def setup_gps_icon(self):
        """Carica l'icona sia in modalità script che dentro l'eseguibile PyInstaller."""
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
        
        # Configurazione Stile Tabella (Treeview) scuro stile dashboard
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

        # --- TOP BAR: Logo / Titolo Applicazione ---
        top_bar = tk.Frame(self.root, bg="#121417", padx=15, pady=10)
        top_bar.pack(fill="x")

        tk.Label(top_bar, text="✈  MB339-NAV-FS", fg="#ffb000", bg="#121417", font=("Segoe UI", 12, "bold")).pack(side="left")
        
        self.btn_howto = tk.Button(top_bar, text="HOW TO", command=self.toggle_howto, bg="#646695", fg="#ffffff", activebackground="#787ab0", activeforeground="#ffffff", font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=2)
        self.btn_howto.pack(side="right", padx=5)

        # --- FRAME 1: Configurazione SimBrief, File PLN & Connessione ---
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

        btn_sb = tk.Button(cfg_frame, text="Scarica OFP", command=self.load_simbrief, bg="#0066cc", fg="white", activebackground="#0055aa", activeforeground="white", font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=4)
        btn_sb.grid(row=0, column=2, padx=5, pady=5)

        btn_pln = tk.Button(cfg_frame, text="Carica .PLN", command=self.load_pln_file, bg="#d97706", fg="white", activebackground="#b45309", activeforeground="white", font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=4)
        btn_pln.grid(row=0, column=3, padx=5, pady=5)

        self.btn_conn = tk.Button(cfg_frame, text="Connetti MSFS", command=self.connect_msfs, bg="#2d6a2e", fg="white", activebackground="#235423", activeforeground="white", font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=4)
        self.btn_conn.grid(row=0, column=4, padx=5, pady=5)

        self.lbl_status = tk.Label(cfg_frame, text="● Stato: Disconnesso da MSFS", fg="#ff5555", bg="#1a1d24", font=("Segoe UI", 9))
        self.lbl_status.grid(row=1, column=0, columnspan=5, pady=(8, 0), sticky="w")

        # --- FRAME 2: Display Digitale Stile Radio/GPS (LED Panel) ---
        nav_frame = tk.Frame(self.root, bg="#0b0c0e", bd=1, relief="solid", highlightbackground="#262b36", highlightthickness=1, padx=15, pady=12)
        nav_frame.pack(fill="x", padx=15, pady=8)

        tk.Label(nav_frame, text="ACTIVE WAYPOINT", fg="#636e7b", bg="#0b0c0e", font=("Consolas", 8, "bold")).grid(row=0, column=0, sticky="w")
        tk.Label(nav_frame, text="BEARING (HDG)", fg="#636e7b", bg="#0b0c0e", font=("Consolas", 8, "bold")).grid(row=0, column=1)
        tk.Label(nav_frame, text="DISTANCE (NM)", fg="#636e7b", bg="#0b0c0e", font=("Consolas", 8, "bold")).grid(row=0, column=2, sticky="e")

        self.lbl_wp_name = tk.Label(nav_frame, text="---", fg="#ffb000", bg="#0b0c0e", font=("Consolas", 24, "bold"))
        self.lbl_wp_name.grid(row=1, column=0, sticky="w", pady=(2, 0))

        self.lbl_brg = tk.Label(nav_frame, text="---°", fg="#ffb000", bg="#0b0c0e", font=("Consolas", 24, "bold"))
        self.lbl_brg.grid(row=1, column=1, padx=45, pady=(2, 0))

        self.lbl_dist = tk.Label(nav_frame, text="--.-", fg="#ffb000", bg="#0b0c0e", font=("Consolas", 24, "bold"))
        self.lbl_dist.grid(row=1, column=2, sticky="e", pady=(2, 0))

        # Separatore visivo interno
        sep = tk.Frame(nav_frame, bg="#1a1d24", height=1)
        sep.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(8, 6))

        self.lbl_pos = tk.Label(nav_frame, text="GPS POS: LAT --.----  |  LON --.----", fg="#3399ff", bg="#0b0c0e", font=("Consolas", 9, "bold"))
        self.lbl_pos.grid(row=3, column=0, columnspan=3, sticky="w")

        # --- FRAME 3: Tabella Waypoint Rotta (Stile Scuro) ---
        list_frame = tk.Frame(self.root, bg="#121417")
        list_frame.pack(fill="both", expand=True, padx=15, pady=5)

        columns = ("idx", "ident", "lat", "lon", "dist")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=11, selectmode="browse", style="Dark.Treeview")
        self.tree.heading("idx", text="#")
        self.tree.heading("ident", text="Waypoint")
        self.tree.heading("lat", text="Latitudine")
        self.tree.heading("lon", text="Longitudine")
        self.tree.heading("dist", text="Distanza (NM)")

        self.tree.column("idx", width=45, anchor="center")
        self.tree.column("ident", width=130, anchor="center")
        self.tree.column("lat", width=150, anchor="center")
        self.tree.column("lon", width=150, anchor="center")
        self.tree.column("dist", width=150, anchor="center")

        # Disattiva interazione mouse sulla tabella
        self.tree.bind("<Button-1>", lambda e: "break")
        self.tree.bind("<ButtonRelease-1>", lambda e: "break")
        self.tree.bind("<B1-Motion>", lambda e: "break")
        self.tree.bind("<Double-1>", lambda e: "break")
        self.tree.bind("<Key>", lambda e: "break")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- FRAME 4: Controlli di Navigazione e Uscita ---
        ctrl_frame = tk.Frame(self.root, bg="#1a1d24", bd=0, padx=12, pady=12)
        ctrl_frame.pack(fill="x", padx=15, pady=10)

        btn_prev = tk.Button(ctrl_frame, text="<< WP Prec.", command=self.prev_wp, bg="#262b36", fg="#e0e0e0", activebackground="#333b4d", activeforeground="white", font=("Segoe UI", 9, "bold"), width=12, relief="flat", pady=6)
        btn_prev.pack(side="left", padx=4)

        self.btn_nav = tk.Button(ctrl_frame, text="AVVIA NAV (HDG)", command=self.toggle_nav, bg="#ffb000", fg="#121417", activebackground="#ffc833", activeforeground="#121417", font=("Segoe UI", 10, "bold"), width=20, relief="flat", pady=6)
        self.btn_nav.pack(side="left", expand=True, padx=4)

        btn_next = tk.Button(ctrl_frame, text="WP Succ. >>", command=self.next_wp, bg="#262b36", fg="#e0e0e0", activebackground="#333b4d", activeforeground="white", font=("Segoe UI", 9, "bold"), width=12, relief="flat", pady=6)
        btn_next.pack(side="left", padx=4)

        btn_exit = tk.Button(ctrl_frame, text="ESCI", command=self.quit_app, bg="#a83232", fg="white", activebackground="#c53f3f", activeforeground="white", font=("Segoe UI", 9, "bold"), width=9, relief="flat", pady=6)
        btn_exit.pack(side="right", padx=4)

    def toggle_howto(self):
        if self.howto_win is not None and tk.Toplevel.winfo_exists(self.howto_win):
            self.howto_win.destroy()
            self.howto_win = None
        else:
            self.howto_win = tk.Toplevel(self.root)
            self.howto_win.title("HOW TO - MB-339 Cockpit Setup & Guida")
            
            x = self.root.winfo_rootx()
            y = self.root.winfo_rooty()
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            
            # Altezza aumentata di 80px per mostrare tutte le righe senza scroll
            howto_height = height + 80
            self.howto_win.geometry(f"680x{howto_height}+{x + width + 10}+{max(10, y - 30)}")
            self.howto_win.configure(bg="#121417")
            self.howto_win.resizable(False, False)
            
            self.howto_win.protocol("WM_DELETE_WINDOW", self.close_howto)

            header_lbl = tk.Label(
                self.howto_win, 
                text="GUIDA OPERATIVA & COCKPIT SETUP", 
                fg="#ffb000", 
                bg="#121417", 
                font=("Segoe UI", 13, "bold")
            )
            header_lbl.pack(pady=(15, 8), padx=20, anchor="w")

            instructions = (
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
            )

            txt_box = tk.Text(
                self.howto_win, 
                wrap="word", 
                bg="#0b0c0e", 
                fg="#e0e0e0", 
                font=("Consolas", 11), 
                padx=15, 
                pady=15, 
                bd=0, 
                highlightthickness=1,
                highlightbackground="#262b36"
            )
            txt_box.insert("1.0", instructions)
            txt_box.config(state="disabled")
            txt_box.pack(fill="both", expand=True, padx=20, pady=8)

            btn_close = tk.Button(
                self.howto_win, 
                text="CHIUDI GUIDA", 
                command=self.close_howto, 
                bg="#a83232", 
                fg="white", 
                font=("Segoe UI", 10, "bold"), 
                relief="flat", 
                padx=20, 
                pady=8
            )
            btn_close.pack(pady=(5, 15))

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
        if self.simbrief_user.get().strip():
            self.entry_sb.config(show="*")

    def quit_app(self):
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
        """
        Converte una stringa <WorldPosition> di MSFS (es. N45° 58' 42.96",E13° 2' 58.92",+000200.00)
        oppure coordinate decimali separate da virgola in (lat, lon) float.
        """
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

    def fetch_simbrief_coords_map(self):
        """
        Scarica un dizionario {IDENT: (lat, lon)} dall'ultimo OFP di SimBrief dell'utente
        per risolvere istantaneamente i file .pln MSFS 2024 privi di tag <WorldPosition>.
        """
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

    def load_pln_file(self):
        """Apre una finestra di dialogo per caricare un file .pln (MSFS 2020 e MSFS 2024)."""
        file_path = filedialog.askopenfilename(
            title="Seleziona Piano di Volo MSFS (.pln)",
            filetypes=[("MSFS Flight Plan", "*.pln"), ("Tutti i file", "*.*")]
        )
        if not file_path:
            return

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            wps = []

            # Verifica se siamo in presenza di un file .pln MSFS 2024 (AppVersionMajor 12) senza WorldPosition
            has_world_pos = root.find(".//WorldPosition") is not None
            sb_coords = {} if has_world_pos else self.fetch_simbrief_coords_map()

            # 1. Nel formato MSFS 2024 <DepartureID> è fuori da <ATCWaypoint>
            dep_node = root.find(".//DepartureID")
            if dep_node is not None and dep_node.text:
                dep_id = dep_node.text.strip().upper()
                if dep_id in sb_coords:
                    lat, lon = sb_coords[dep_id]
                    wps.append({"name": dep_id, "lat": lat, "lon": lon})

            # 2. Scorre tutti i blocchi <ATCWaypoint>
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

                # Caso A: Tag standard <WorldPosition> (MSFS 2020 / Little Navmap)
                wp_pos = wp_elem.find("WorldPosition")
                if wp_pos is not None and wp_pos.text:
                    lat, lon = self.parse_world_position(wp_pos.text)

                # Caso B: Tag <Latitude> e <Longitude>
                if lat is None or lon is None:
                    lat_node = wp_elem.find(".//Latitude")
                    lon_node = wp_elem.find(".//Longitude")
                    if lat_node is not None and lon_node is not None and lat_node.text and lon_node.text:
                        try:
                            lat = float(lat_node.text.strip())
                            lon = float(lon_node.text.strip())
                        except ValueError:
                            pass

                # Caso C: Formato MSFS 2024 senza coordinate (risolto tramite mappa SimBrief)
                if (lat is None or lon is None) and ident.upper() in sb_coords:
                    lat, lon = sb_coords[ident.upper()]

                if lat is not None and lon is not None and (lat != 0.0 or lon != 0.0):
                    if not wps or wps[-1]["name"] != ident:
                        wps.append({"name": ident, "lat": lat, "lon": lon})

            # 3. Nel formato MSFS 2024 <DestinationID> è fuori da <ATCWaypoint>
            dest_node = root.find(".//DestinationID")
            if dest_node is not None and dest_node.text:
                dest_id = dest_node.text.strip().upper()
                if dest_id in sb_coords:
                    lat, lon = sb_coords[dest_id]
                    if not wps or wps[-1]["name"] != dest_id:
                        wps.append({"name": dest_id, "lat": lat, "lon": lon})

            if not wps:
                messagebox.showwarning(
                    "Coordinate Mancanti nel file .PLN",
                    "Questo file .pln (formato MSFS 2024) contiene solo i nomi dei waypoint senza coordinate geografiche.\n\n"
                    "Assicurati che il tuo SimBrief ID sia inserito correttamente o esporta il file in formato 'FS2020 (.pln)' da SimBrief / Little Navmap."
                )
                return

            self.waypoints = wps
            self.current_wp_index = 1 if len(wps) > 1 else 0
            self.refresh_tree()

            active_wp = self.waypoints[self.current_wp_index]
            if self.plane_lat is not None and self.plane_lon is not None:
                brg = self.calculate_bearing(self.plane_lat, self.plane_lon, active_wp["lat"], active_wp["lon"])
                dist_nm = self.calculate_distance_nm(self.plane_lat, self.plane_lon, active_wp["lat"], active_wp["lon"])
                self.update_telemetry_ui(active_wp["name"], brg, dist_nm)
            else:
                self.lbl_wp_name.config(text=active_wp["name"])
                self.lbl_brg.config(text="---°")
                self.lbl_dist.config(text="--.-")

        except Exception as e:
            messagebox.showerror("Errore Caricamento PLN", f"Impossibile leggere il file .pln:\n{e}")

    def load_simbrief(self):
        user = self.simbrief_user.get().strip()
        if not user:
            messagebox.showwarning("Attenzione", "Inserisci il tuo SimBrief Pilot ID.")
            return

        self.schedule_id_mask()

        url = f"https://www.simbrief.com/api/xml.fetcher.php?userid={user}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                wps = []

                orig = root.find(".//origin")
                if orig is not None:
                    icao = orig.find("icao_code")
                    lat = orig.find("pos_lat") if orig.find("pos_lat") is not None else orig.find("lat")
                    lon = orig.find("pos_long") if orig.find("pos_long") is not None else orig.find("lon")
                    if icao is not None and lat is not None and lon is not None:
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

                dest = root.find(".//destination")
                if dest is not None:
                    icao = dest.find("icao_code")
                    lat = dest.find("pos_lat") if dest.find("pos_lat") is not None else dest.find("lat")
                    lon = dest.find("pos_long") if dest.find("pos_long") is not None else dest.find("lon")
                    if icao is not None and lat is not None and lon is not None:
                        if not wps or wps[-1]["name"] != icao.text:
                            wps.append({"name": icao.text, "lat": float(lat.text), "lon": float(lon.text)})

                self.waypoints = wps
                self.current_wp_index = 1 if len(wps) > 1 else 0
                self.refresh_tree()

                if self.waypoints:
                    active_wp = self.waypoints[self.current_wp_index]
                    if self.plane_lat is not None and self.plane_lon is not None:
                        brg = self.calculate_bearing(self.plane_lat, self.plane_lon, active_wp["lat"], active_wp["lon"])
                        dist_nm = self.calculate_distance_nm(self.plane_lat, self.plane_lon, active_wp["lat"], active_wp["lon"])
                        self.update_telemetry_ui(active_wp["name"], brg, dist_nm)
                    else:
                        self.lbl_wp_name.config(text=active_wp["name"])
            else:
                messagebox.showerror("Errore SimBrief", f"Errore HTTP: {response.status_code}")
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile scaricare il piano da SimBrief:\n{e}")

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
            self.lbl_status.config(text="● Stato: Connesso a MSFS (SimConnect Attivo)", fg="#4ec9b0")
            self.btn_conn.config(text="Riconnetti MSFS", bg="#235423")
        except Exception as e:
            self.connected = False
            self.lbl_status.config(text="● Stato: Errore connessione MSFS", fg="#ff5555")
            messagebox.showerror("Errore SimConnect", f"Assicurati che MSFS sia aperto.\nDettaglio: {e}")

    def toggle_nav(self):
        if not self.connected:
            messagebox.showwarning("Non Connesso", "Connettiti prima a MSFS!")
            return
        if not self.waypoints:
            messagebox.showwarning("Nessuna Rotta", "Scarica prima il piano da SimBrief o carica un file .PLN!")
            return

        self.nav_active = not self.nav_active
        if self.nav_active:
            self.btn_nav.config(text="NAV ATTIVA (STOP)", bg="#4ec9b0", fg="#121417")
            try:
                if self.ev_hdg_hold:
                    self.ev_hdg_hold()
            except Exception:
                pass
        else:
            self.btn_nav.config(text="AVVIA NAV (HDG)", bg="#ffb000", fg="#121417")

    def prev_wp(self):
        if self.waypoints and self.current_wp_index > 0:
            self.current_wp_index -= 1
            self.refresh_tree()

    def next_wp(self):
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
        while self.running:
            if self.connected and self.aq:
                try:
                    p_lat = self.aq.get("PLANE_LATITUDE")
                    p_lon = self.aq.get("PLANE_LONGITUDE")

                    if p_lat is not None and p_lon is not None and p_lat != 0.0:
                        self.plane_lat = p_lat
                        self.plane_lon = p_lon
                        
                        self.root.after(0, self.lbl_pos.config, {"text": f"GPS POS: LAT {p_lat:.4f}  |  LON {p_lon:.4f}"})

                        if self.waypoints and self.current_wp_index < len(self.waypoints):
                            target = self.waypoints[self.current_wp_index]
                            brg = self.calculate_bearing(p_lat, p_lon, target["lat"], target["lon"])
                            dist_nm = self.calculate_distance_nm(p_lat, p_lon, target["lat"], target["lon"])

                            self.root.after(0, self.update_telemetry_ui, target["name"], brg, dist_nm)

                            update_counter += 1
                            if update_counter >= 3:
                                update_counter = 0
                                self.root.after(0, self.refresh_tree)

                            if self.nav_active:
                                if self.ev_hdg_set:
                                    try:
                                        self.ev_hdg_set(int(round(brg)))
                                    except Exception:
                                        pass

                                if dist_nm < 0.8:
                                    if self.current_wp_index < len(self.waypoints) - 1:
                                        self.current_wp_index += 1
                                        self.root.after(0, self.refresh_tree)
                                    else:
                                        self.nav_active = False
                                        self.root.after(0, self.btn_nav.config, {"text": "ROTTA COMPLETATA", "bg": "#4ec9b0", "fg": "#121417"})
                except Exception:
                    pass
            time.sleep(1)

    def update_telemetry_ui(self, name, brg, dist_nm):
        self.lbl_wp_name.config(text=name)
        self.lbl_brg.config(text=f"{int(round(brg)):03d}°")
        self.lbl_dist.config(text=f"{dist_nm:.1f}")


if __name__ == "__main__":
    root = tk.Tk()
    app = MB339NavApp(root)
    root.mainloop()