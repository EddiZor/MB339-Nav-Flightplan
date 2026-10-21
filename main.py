import time
import math
import requests
import xml.etree.ElementTree as ET
from SimConnect import *

# Inserisci il tuo SimBrief Pilot ID
SIMBRIEF_USER = "312844"

def fetch_simbrief_flightplan_xml(user):
    """Scarica e analizza l'ultimo piano di volo direttamente dall'API XML di SimBrief."""
    url = f"https://www.simbrief.com/api/xml.fetcher.php?userid={user}"
    print(f"Connessione a SimBrief per il recupero dell'OFP (ID: {user})...")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code ricevuto: {response.status_code}")
        
        if response.status_code == 200:
            # Parsing dell'XML ricevuto da SimBrief
            root = ET.fromstring(response.content)
            
            waypoints = []
            
            # Estrai aeroporto di partenza
            orig_elem = root.find(".//origin")
            if orig_elem is not None:
                icao = orig_elem.find("icao_code")
                lat = orig_elem.find("lat")
                lon = orig_elem.find("lon")
                if icao is not None and lat is not None and lon is not None:
                    waypoints.append({
                        "name": icao.text,
                        "lat": float(lat.text),
                        "lon": float(lon.text)
                    })
            
            # Estrai tutti i waypoint di rotta dal navlog
            for fix in root.findall(".//navlog/fix"):
                ident = fix.find("ident")
                lat = fix.find("lat")
                lon = fix.find("lon")
                
                if ident is not None and lat is not None and lon is not None:
                    try:
                        lat_val = float(lat.text)
                        lon_val = float(lon.text)
                        if lat_val != 0.0 and lon_val != 0.0:
                            # Evitiamo doppioni consecutivi identici
                            if not waypoints or waypoints[-1]["name"] != ident.text:
                                waypoints.append({
                                    "name": ident.text,
                                    "lat": lat_val,
                                    "lon": lon_val
                                })
                    except (ValueError, TypeError):
                        continue
            
            # Estrai aeroporto di arrivo (se non già presente alla fine)
            dest_elem = root.find(".//destination")
            if dest_elem is not None:
                icao = dest_elem.find("icao_code")
                lat = dest_elem.find("lat")
                lon = dest_elem.find("lon")
                if icao is not None and lat is not None and lon is not None:
                    if not waypoints or waypoints[-1]["name"] != icao.text:
                        waypoints.append({
                            "name": icao.text,
                            "lat": float(lat.text),
                            "lon": float(lon.text)
                        })
            
            print(f"Piano di volo scaricato con successo da SimBrief! ({len(waypoints)} punti totali trovati)")
            return waypoints
        else:
            print(f"Errore HTTP da SimBrief: {response.status_code}")
            return []
    except Exception as e:
        print(f"Errore di connessione o parsing XML con SimBrief: {e}")
        return []

def calculate_bearing(lat1, lon1, lat2, lon2):
    """Calcola la rotta (in gradi) tra due punti geografici."""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dLon = lon2 - lon1
    x = math.sin(dLon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dLon)
    bearing = math.degrees(math.atan2(x, y))
    return (bearing + 360) % 360

# 1. Recupero dati in remoto da SimBrief
waypoints = fetch_simbrief_flightplan_xml(SIMBRIEF_USER)

if not waypoints:
    print("Impossibile procedere: nessun waypoint recuperato da SimBrief. Assicurati di aver generato un volo sul sito.")
    exit()

print("Waypoint della rotta:")
for wp in waypoints:
    print(f" - {wp['name']} ({wp['lat']}, {wp['lon']})")

# 2. Inizializzazione SimConnect per MSFS
print("\nConnessione a Microsoft Flight Simulator in corso...")
sm = SimConnect()
aq = AircraftRequests(sm, _time=1000)
ae = AircraftEvents(sm)

current_wp_index = 0
print(f"Inizio navigazione automatica per {len(waypoints)} waypoint...")

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