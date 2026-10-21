import os
import sys
import subprocess

def install_and_import(package, import_name=None):
    if import_name is None:
        import_name = package
    try:
        __import__(import_name)
    except ImportError:
        print(f"Installazione di {package} in corso...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Verifica dipendenze
install_and_import("pillow", "PIL")
install_and_import("pyinstaller", "PyInstaller")

from PIL import Image
import SimConnect

# Percorsi assoluti puliti
base_dir = os.path.dirname(os.path.abspath(__file__))
ico_path = os.path.join(base_dir, "gps_icon.ico")
main_path = os.path.join(base_dir, "main.py")

print("Generazione icona gps_icon.ico...")
img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
# (Se vuoi puoi rigenerare l'immagine o usare la tua esistente)
img.save(ico_path, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])

# Trova la DLL di SimConnect
sc_dir = os.path.dirname(SimConnect.__file__)
dll_path = os.path.join(sc_dir, "SimConnect.dll")

# Comando PyInstaller pulito (senza liste nell'icona)
cmd = [
    sys.executable, "-m", "PyInstaller",
    "--noconsole",
    "--onefile",
    f"--icon={ico_path}",
    f"--add-data={ico_path}{os.pathsep}.",
    "--name=MB339-Nav-Flightplan",
    "--clean",
    "--noconfirm" # Sovrascrive la vecchia .spec senza chiedere conferma
]

if os.path.exists(dll_path):
    print(f"Trovata libreria nativa: {dll_path}")
    cmd.append(f"--add-binary={dll_path}{os.pathsep}SimConnect")
    cmd.append(f"--add-data={dll_path}{os.pathsep}SimConnect")

cmd.append(main_path)

print("\nAvvio compilazione dell'eseguibile con PyInstaller...")
subprocess.check_call(cmd)

print("\n=======================================================")
print("COMPILAZIONE COMPLETATA CON SUCCESSO!")
print("Trovi il tuo file eseguibile pronto all'uso in:")
print(os.path.join(base_dir, "dist", "MB339-Nav-Flightplan.exe"))
print("=======================================================")