import os
import sys
import subprocess
import shutil
import zipfile

# Definisci qui la versione corrente dell'applicazione per aggiornare automaticamente lo ZIP
APP_VERSION = "2.1"
# Assicurati che questo sia il nome esatto del tuo script Python principale
MAIN_SCRIPT = "MB339-Nav-Flightplan.py"

def build():
    print(f"=== Avvio compilazione e pacchettizzazione per Flightsim.to (v{APP_VERSION}) ===")
    
    # 1. Pulisci le build precedenti
    for d in ["build", "dist"]:
        if os.path.exists(d):
            shutil.rmtree(d)
            print(f"Rimossa cartella temporanea: {d}")

    # 2. Trova la SimConnect.dll nel pacchetto installato di Python
    simconnect_dll_path = None
    try:
        import SimConnect
        sc_dir = os.path.dirname(SimConnect.__file__)
        dll_candidate = os.path.join(sc_dir, "SimConnect.dll")
        if os.path.exists(dll_candidate):
            simconnect_dll_path = dll_candidate
    except Exception:
        pass

    # 3. Comando PyInstaller ottimizzato
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        "--name=MB339-Nav-Flightplan",
        "--icon=gps_icon.ico",
        "--clean"
    ]

    # Include automaticamente i metadati della versione nell'EXE se il file esiste
    if os.path.exists("version.txt"):
        cmd.append("--version-file=version.txt")
        print("Incluso file metadati version.txt")

    if simconnect_dll_path:
        cmd.append(f"--add-binary={simconnect_dll_path};SimConnect")
        print(f"Inclusa SimConnect.dll da: {simconnect_dll_path}")

    cmd.append(MAIN_SCRIPT)

    print("Esecuzione PyInstaller in corso...")
    subprocess.check_call(cmd)

    # 4. Creazione archivio ZIP per Flightsim.to
    dist_dir = "dist"
    zip_name = f"MB339-Nav-Flightplan-v{APP_VERSION}.zip"
    zip_path = os.path.join(dist_dir, zip_name)

    print(f"Creazione archivio di rilascio: {zip_path}")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Aggiunge l'eseguibile
        exe_file = "MB339-Nav-Flightplan.exe"
        exe_full_path = os.path.join(dist_dir, exe_file)
        if os.path.exists(exe_full_path):
            zipf.write(exe_full_path, arcname=exe_file)
            print(f"  + Aggiunto: {exe_file}")

        # Aggiunge il README.md se presente
        if os.path.exists("README.md"):
            zipf.write("README.md", arcname="README.md")
            print("  + Aggiunto: README.md")

    print("\n=== Operazione completata con successo! ===")
    print(f"Archivio ZIP pronto per Flightsim.to: {zip_path}")

if __name__ == "__main__":
    build()