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

# 1. Verifica che Pillow e PyInstaller siano installati
install_and_import("pillow", "PIL")
install_and_import("pyinstaller", "PyInstaller")

from PIL import Image, ImageDraw
import SimConnect

# 2. Genera il file gps_icon.ico ad alta risoluzione (Multi-size ICO)
ico_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gps_icon.ico")
print("Generazione icona gps_icon.ico...")

img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Quadrante esterno scuro con bordo verde avionica
draw.ellipse((16, 16, 240, 240), fill=(20, 20, 20, 255), outline=(0, 255, 102, 255), width=12)
# Cerchio interno telemetria
draw.ellipse((68, 68, 188, 188), outline=(0, 140, 60, 255), width=4)
# Reticolo bussola / GPS
draw.line((128, 28, 128, 228), fill=(0, 180, 80, 255), width=6)
draw.line((28, 128, 228, 128), fill=(0, 180, 80, 255), width=6)
# Freccia direzionale del Waypoint (verde brillante)
draw.polygon([(128, 44), (92, 164), (128, 140), (164, 164)], fill=(0, 255, 102, 255))
# Punto centrale rosso
draw.ellipse((114, 114, 142, 142), fill=(255, 60, 60, 255))

img.save(ico_path, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
print(f"Icona creata con successo: {ico_path}")

# 3. Trova il percorso di SimConnect.dll per includerlo nell'eseguibile
sc_dir = os.path.dirname(SimConnect.__file__)
dll_path = os.path.join(sc_dir, "SimConnect.dll")

# 4. Configura ed esegui PyInstaller
cmd = [
    sys.executable, "-m", "PyInstaller",
    "--noconsole",
    "--onefile",
    f"--icon={ico_path}",
    f"--add-data={ico_path};.",
    "--name=MB339-Nav-Flightplan",
    "--clean"
]

if os.path.exists(dll_path):
    print(f"Trovata libreria nativa: {dll_path}")
    cmd.append(f"--add-binary={dll_path};SimConnect")
    cmd.append(f"--add-data={dll_path};SimConnect")

cmd.append("main.py")

print("\nAvvio compilazione dell'eseguibile con PyInstaller...")
subprocess.check_call(cmd)
print("\n=======================================================")
print("COMPILAZIONE COMPLETATA CON SUCCESSO!")
print("Trovi il tuo file eseguibile pronto all'uso in:")
print(os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist", "MB339-Nav-Flightplan.exe"))
print("=======================================================")