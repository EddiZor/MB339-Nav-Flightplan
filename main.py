import os
import sys
import time
import math
import ctypes
import threading
import requests
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import ttk, messagebox
from SimConnect import *

# Imposta l'AppUserModelID su Windows affinché l'icona appaia nella barra delle applicazioni
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("eddizor.mb339.simbrief.nav")
except Exception:
    pass


class MB339NavApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MB-339 SimBrief GPS Nav System")
        self.root.geometry("560x690")
        self.root.configure(bg="#1e1e1e")
        self.root.resizable(False, False)

        # Intercetta la chiusura della finestra dalla "X" in alto a destra
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

        # Imposta e genera l'icona GPS
        self.setup_gps_icon()

        # Variabili di stato
        self.simbrief_user = tk.StringVar(value="******")
        self.mask_timer = None
        self.waypoints = []
        self.current_wp_index = 0
        self.nav_active = False
        self.connected = False
        self.howto_win = None  # Riferimento alla finestra di istruzioni

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

        # Disegna l'icona 32x32 in memoria con PhotoImage
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

        # --- FRAME 1: Configurazione SimBrief & SimConnect ---
        top_frame = tk.Frame(self.root, bg="#252526", bd=1, relief="ridge", padx=10, pady=10)
        top_frame.pack(fill="x", padx=12, pady=10)

        tk.Label(top_frame, text="SimBrief ID:", fg="#d4d4d4", bg="#252526", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.entry_sb = tk.Entry(
            top_frame,
            textvariable=self.simbrief_user,
            width=10,
            font=("Consolas", 11),
            bg="#3c3c3c",
            fg="#ffffff",
            insertbackground="white"
        )
        self.entry_sb.grid(row=0, column=1, padx=4, pady=5)

        self.entry_sb.bind("<KeyRelease>", self.on_id_activity)
        self.entry_sb.bind("<FocusIn>", self.on_id_activity)

        btn_sb = tk.Button(top_frame, text="Scarica OFP", command=self.load_simbrief, bg="#007acc", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", padx=6, pady=4)
        btn_sb.grid(row=0, column=2, padx=4, pady=5)

        self.btn_conn = tk.Button(top_frame, text="Connetti MSFS", command=self.connect_msfs, bg="#388a34", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", padx=6, pady=4)
        self.btn_conn.grid(row=0, column=3, padx=4, pady=5)

        # Pulsante HOW TO
        self.btn_howto = tk.Button(top_frame, text="HOW TO", command=self.toggle_howto, bg="#646695", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", padx=6, pady=4)
        self.btn_howto.grid(row=0, column=4, padx=4, pady=5)

        self.lbl_status = tk.Label(top_frame, text="Stato: Disconnesso da MSFS", fg="#f48771", bg="#252526", font=("Segoe UI", 9, "italic"))
        self.lbl_status.grid(row=1, column=0, columnspan=5, pady=(5, 0), sticky="w")

        # --- FRAME 2: Display Dati Navigazione (Stile Avionica GPS) ---
        nav_frame = tk.Frame(self.root, bg="#141414", bd=2, relief="sunken", padx=15, pady=12)
        nav_frame.pack(fill="x", padx=12, pady=5)

        tk.Label(nav_frame, text="ACTIVE WAYPOINT", fg="#808080", bg="#141414", font=("Consolas", 9, "bold")).grid(row=0, column=0, sticky="w")
        tk.Label(nav_frame, text="BRG (HDG)", fg="#808080", bg="#141414", font=("Consolas", 9, "bold")).grid(row=0, column=1)
        tk.Label(nav_frame, text="DIST (NM)", fg="#808080", bg="#141414", font=("Consolas", 9, "bold")).grid(row=0, column=2, sticky="e")

        self.lbl_wp_name = tk.Label(nav_frame, text="---", fg="#00ff66", bg="#141414", font=("Consolas", 22, "bold"))
        self.lbl_wp_name.grid(row=1, column=0, sticky="w", pady=2)

        self.lbl_brg = tk.Label(nav_frame, text="---°", fg="#00ff66", bg="#141414", font=("Consolas", 22, "bold"))
        self.lbl_brg.grid(row=1, column=1, padx=40, pady=2)

        self.lbl_dist = tk.Label(nav_frame, text="--.-", fg="#00ff66", bg="#141414", font=("Consolas", 22, "bold"))
        self.lbl_dist.grid(row=1, column=2, sticky="e", pady=2)

        self.lbl_pos = tk.Label(nav_frame, text="POS: LAT --.----  |  LON --.----", fg="#569cd6", bg="#141414", font=("Consolas", 10))
        self.lbl_pos.grid(row=2, column=0, columnspan=3, pady=(8, 0), sticky="w")

        # --- FRAME 3: Tabella Waypoint Rotta ---
        list_frame = tk.Frame(self.root, bg="#1e1e1e")
        list_frame.pack(fill="both", expand=True, padx=12, pady=8)

        columns = ("idx", "ident", "lat", "lon")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=11)
        self.tree.heading("idx", text="#")
        self.tree.heading("ident", text="Waypoint")
        self.tree.heading("lat", text="Latitudine")
        self.tree.heading("lon", text="Longitudine")

        self.tree.column("idx", width=45, anchor="center")
        self.tree.column("ident", width=130, anchor="center")
        self.tree.column("lat", width=150, anchor="center")
        self.tree.column("lon", width=150, anchor="center")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- FRAME 4: Controlli Autopilota, Sequenza e Uscita ---
        ctrl_frame = tk.Frame(self.root, bg="#252526", bd=1, relief="ridge", padx=10, pady=10)
        ctrl_frame.pack(fill="x", padx=12, pady=10)

        btn_prev = tk.Button(ctrl_frame, text="<< WP Prec.", command=self.prev_wp, bg="#3c3c3c", fg="white", font=("Segoe UI", 9, "bold"), width=11, relief="flat", pady=5)
        btn_prev.pack(side="left", padx=4)

        self.btn_nav = tk.Button(ctrl_frame, text="AVVIA NAV (HDG)", command=self.toggle_nav, bg="#ce9178", fg="#1e1e1e", font=("Segoe UI", 10, "bold"), width=18, relief="flat", pady=5)
        self.btn_nav.pack(side="left", expand=True, padx=4)

        btn_next = tk.Button(ctrl_frame, text="WP Succ. >>", command=self.next_wp, bg="#3c3c3c", fg="white", font=("Segoe UI", 9, "bold"), width=11, relief="flat", pady=5)
        btn_next.pack(side="left", padx=4)

        btn_exit = tk.Button(ctrl_frame, text="ESCI", command=self.quit_app, bg="#c72e2e", fg="white", font=("Segoe UI", 9, "bold"), width=8, relief="flat", pady=5)
        btn_exit.pack(side="right", padx=4)

    def toggle_howto(self):
        """Apre o chiude la finestra HOW TO a destra della finestra principale."""
        if self.howto_win is not None and tk.Toplevel.winfo_exists(self.howto_win):
            # Se la finestra è già aperta, la chiude
            self.howto_win.destroy()
            self.howto_win = None
        else:
            # Altrimenti la crea e la posiziona a destra
            self.howto_win = tk.Toplevel(self.root)
            self.howto_win.title("HOW TO - MB-339 Cockpit Setup")
            
            x = self.root.winfo_rootx()
            y = self.root.winfo_rooty()
            width = self.root.winfo_width()
            
            self.howto_win.geometry(f"520x460+{x + width + 10}+{y}")
            self.howto_win.configure(bg="#252526")
            self.howto_win.resizable(False, False)
            
            # Intercetta la chiusura con la "X" per azzerare il riferimento
            self.howto_win.protocol("WM_DELETE_WINDOW", self.close_howto)

            header_lbl = tk.Label(
                self.howto_win, 
                text="Istruzioni Operative per il Cockpit (MB-339)", 
                fg="#4ec9b0", 
                bg="#252526", 
                font=("Segoe UI", 11, "bold")
            )
            header_lbl.pack(pady=(15, 10), padx=15, anchor="w")

            instructions = (
                "1. PREPARAZIONE AUTOPILOTA & FLIGHT DIRECTOR:\n"
                "   • Individua il pannello del Flight Director / Autopilota sul glareshield centrale.\n"
                "   • Assicurati che l'autopilota sia inserito (Master ON).\n"
                "   • Premi il pulsante HDG (Heading) sul pannello per fare in modo che\n"
                "     l'aeromobile segua la prua impostata dal bug di direzione.\n"
                "   • Se desideri mantenere la quota di crociera, inserisci ALT HOLD\n"
                "     una volta raggiunto il livello di volo desiderato.\n\n"
                "2. SINCRONIZZAZIONE E AVVIO DELLA NAVIGAZIONE:\n"
                "   • Inserisci il tuo SimBrief Pilot ID e clicca su 'Scarica OFP'.\n"
                "   • Clicca su 'Connetti MSFS' per attivare il ponte SimConnect.\n"
                "   • Quando sei pronto al decollo o in volo, clicca sul pulsante\n"
                "     centrale 'AVVIA NAV (HDG)' nell'applicazione.\n"
                "   • L'app aggiornerà automaticamente in tempo reale l'Heading Bug\n"
                "     guidando l'MB-339 attraverso tutti i waypoint della rotta."
            )

            txt_box = tk.Text(
                self.howto_win, 
                wrap="word", 
                bg="#1e1e1e", 
                fg="#d4d4d4", 
                font=("Consolas", 10), 
                padx=12, 
                pady=12, 
                bd=0, 
                highlightthickness=0
            )
            txt_box.insert("1.0", instructions)
            txt_box.config(state="disabled")
            txt_box.pack(fill="both", expand=True, padx=15, pady=5)

            btn_close = tk.Button(
                self.howto_win, 
                text="CHIUDI", 
                command=self.close_howto, 
                bg="#007acc", 
                fg="white", 
                font=("Segoe UI", 9, "bold"), 
                relief="flat", 
                padx=15, 
                pady=6
            )
            btn_close.pack(pady=15)

    def close_howto(self):
        """Chiude la finestra HOW TO e pulisce il riferimento."""
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
                messagebox.showinfo("SimBrief OFP", f"Piano di volo caricato correttamente!\n{len(wps)} waypoint estratti.")
            else:
                messagebox.showerror("Errore SimBrief", f"Errore HTTP: {response.status_code}")
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile scaricare il piano da SimBrief:\n{e}")

    def refresh_tree(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for i, wp in enumerate(self.waypoints):
            prefix = "▶ " if i == self.current_wp_index else ""
            self.tree.insert("", "end", iid=str(i), values=(f"{prefix}{i+1}", wp["name"], f"{wp['lat']:.4f}", f"{wp['lon']:.4f}"))
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
            self.lbl_status.config(text="Stato: Connesso a MSFS (SimConnect Attivo)", fg="#4ec9b0")
            self.btn_conn.config(text="Riconnetti MSFS", bg="#2d6a2e")
        except Exception as e:
            self.connected = False
            self.lbl_status.config(text="Stato: Errore connessione MSFS", fg="#f48771")
            messagebox.showerror("Errore SimConnect", f"Assicurati che MSFS sia aperto.\nDettaglio: {e}")

    def toggle_nav(self):
        if not self.connected:
            messagebox.showwarning("Non Connesso", "Connettiti prima a MSFS!")
            return
        if not self.waypoints:
            messagebox.showwarning("Nessuna Rotta", "Scarica prima il piano di volo da SimBrief!")
            return

        self.nav_active = not self.nav_active
        if self.nav_active:
            self.btn_nav.config(text="NAV ATTIVA (STOP)", bg="#4ec9b0", fg="#1e1e1e")
            try:
                if self.ev_hdg_hold:
                    self.ev_hdg_hold()
            except Exception:
                pass
        else:
            self.btn_nav.config(text="AVVIA NAV (HDG)", bg="#ce9178", fg="#1e1e1e")

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
        while self.running:
            if self.connected and self.aq:
                try:
                    p_lat = self.aq.get("PLANE_LATITUDE")
                    p_lon = self.aq.get("PLANE_LONGITUDE")

                    if p_lat is not None and p_lon is not None and p_lat != 0.0:
                        self.root.after(0, self.lbl_pos.config, {"text": f"POS: LAT {p_lat:.4f}  |  LON {p_lon:.4f}"})

                        if self.waypoints and self.current_wp_index < len(self.waypoints):
                            target = self.waypoints[self.current_wp_index]
                            brg = self.calculate_bearing(p_lat, p_lon, target["lat"], target["lon"])
                            dist_nm = self.calculate_distance_nm(p_lat, p_lon, target["lat"], target["lon"])

                            self.root.after(0, self.update_telemetry_ui, target["name"], brg, dist_nm)

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
                                        self.root.after(0, self.btn_nav.config, {"text": "ROTTA COMPLETATA", "bg": "#6a9955"})
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