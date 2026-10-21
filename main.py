import time
import math
import requests
from SimConnect import *

# Inserisci il tuo SimBrief Pilot ID o Username
SIMBRIEF_USER = "312044"  # Puoi usare anche il tuo username es. "Eddi" se preferisci

def fetch_simbrief_flightplan(user):
    """Scarica l'ultimo piano di volo in formato JSON dall'API di SimBrief."""
    url = f"https://www.simbrief.com/api/xml.fetch.php?userid={user}&json=1"
    print(f"Connessione a SimBrief per il recupero del piano di volo (ID: {user})...")
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            waypoints = []
            orig = data.get("origin", {})
            dest = data.get("destination", {})
            
            # Aggiungi aeroporto di partenza come primo punto
            if orig:
                waypoints.append({
                    "name": orig.get("icao_code", "ORIG"),
                    "lat": float(orig.get("lat", 0)),
                    "lon": float(orig.get("lon", 0))
                })
            
            # Estrai i waypoint enroute dal piano di volo SimBrief
            navlog = data.get("navlog", [])
            for fix in navlog:
                # Prendiamo i punti significativi (fix, VOR, NDB, wpt)
                lat = float(fix.get("lat", 0))
                lon = float(fix.get("lon", 0))
                ident = fix.get("ident", "WP")
                
                # Evitiamo duplicati consecutivi o coordinate nulle
                if lat != 0.0 and lon != 0.0:
                    waypoints.append({
                        "name": ident,
                        "lat": lat,
                        "lon": lon
                    })
            
            # Aggiungi aeroporto di arrivo come ultimo punto se non già incluso
            if dest and (not waypoints or waypoints[-1]["name"] != dest.get("icao_code")):
                waypoints.append({
                    "name": dest.get("icao_code", "DEST"),
                    "lat": float(dest.get("lat", 0)),
                    "lon": float(dest.get("lon", 0))
                })
                
            gen_time = data.get("params", {}).get("time_generated", "N/A")
            print(f"Piano di volo scaricato con successo! (Generato il: {gen_time})")
            print(Route := f"Rotta: {orig.get('icao_code')} -> {dest.get('icao_code')} ({len(waypoints)} punti totali)")
            
            return waypoints
        else:
            print(f"Errore HTTP da SimBrief: {response.status_code}")
            return []
    except Exception as e:
        print(f"Errore di connessione a SimBrief: {e}")
        return []

def calculate_bearing(lat1, lon1, lat2, lon2):
    """Calcola la rotta (in gradi) tra due punti geografici."""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dLon = lon2 - lon1
    x = math.sin(dLon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dLon)
    bearing = math.degrees(math.atan2(x, y))
    return (bearing + 360) % 360

# 1. Recupero dati da SimBrief
waypoints = fetch_simbrief_flightplan(SIMBRIEF_USER)

if not waypoints:
    print("Impossibile procedere senza un piano di volo valido da SimBrief.")
    exit()

# 2. Inizializzazione SimConnect
print("Connessione a Microsoft Flight Simulator in corso...")
sm = SimConnect()
aq = AircraftRequests(sm, _time=1000)
ae = AircraftEvents(sm)

current_wp_index = 0
print(f"Inizio navigazione per {len(waypoints)} waypoint...")

# Riferimenti Autopilota
ap_master = ae.find("AUTOPILOT_MASTER")
hdg_hold = ae.find("AP_HDG_HOLD")
hdg_select = ae.find("HEADING_BUG_SET")

# Attiva l'autopilota e la modalità Heading
ap_master.set(1)
hdg_hold.set(1)

print("Autopilota inserito. Sistema di navigazione attivo. Premi Ctrl+C per uscire.")

try:
    while True:
        if current_wp_index >= len(waypoints):
            print("Rotta completata! Destinazione raggiunta.")
            break

        plane_lat = aq.get("PLANE_LATITUDE")
        plane_lon = aq.get("PLANE_LONGITUDE")

        if plane_lat is not None and plane_lon is not None:
            target = waypoints[current_wp_index]
            target_lat = target["lat"]
            target_lon = target["lon"]
            target_name = target["name"]
            
            # Calcola il bearing verso il waypoint corrente
            bearing = calculate_bearing(plane_lat, plane_lon, target_lat, target_lon)
            
            # Imposta l'Heading bug dell'autopilota
            hdg_select.set(int(bearing))
            
            # Calcola distanza approssimativa in gradi (~0.01 = 1 km)
            dist = math.sqrt((plane_lat - target_lat)**2 + (plane_lon - target_lon)**2)
            
            print(f"Verso: {target_name} ({current_wp_index+1}/{len(waypoints)}) | "
                  f"Pos: {plane_lat:.4f}, {plane_lon:.4f} | Heading da tenere: {bearing:.1f}°")

            # Soglia di passaggio al waypoint successivo (~1.5 km)
            if dist < 0.015:
                print(f"--> Waypoint {target_name} raggiunto! Passaggio al successivo.")
                current_wp_index += 1

        time.sleep(1)

except KeyboardInterrupt:
    print("\nNavigazione interrotta dall'utente. Controllo restituito al pilota.")