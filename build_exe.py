import os
import sys
import shutil
import subprocess

base_dir = os.path.dirname(os.path.abspath(__file__))
ico_path = os.path.join(base_dir, "gps_icon.ico")
main_path = os.path.join(base_dir, "main.py")
dist_dir = os.path.join(base_dir, "dist")
build_dir = os.path.join(base_dir, "build")
spec_file = os.path.join(base_dir, "MB339-Nav-Flightplan.spec")

# 1. Chiude forzatamente eventuali istanze di MB339-Nav-Flightplan.exe rimaste aperte
print("Chiusura eventuali istanze aperte dell'applicazione...")
subprocess.run(["taskkill", "/F", "/IM", "MB339-Nav-Flightplan.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# 2. Elimina le vecchie cartelle build/ e dist/ per evitare file in cache
for folder in [dist_dir, build_dir]:
    if os.path.exists(folder):
        shutil.rmtree(folder, ignore_errors=True)
if os.path.exists(spec_file):
    os.remove(spec_file)

# 3. Rigenera l'icona GPS (se non presente o per sicurezza)
from PIL import Image, ImageDraw
import SimConnect

img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)
draw.ellipse((16, 16, 240, 240), fill=(20, 20, 20, 255), outline=(0, 255, 102, 255), width=12)
draw.ellipse((68, 68, 188, 188), outline=(0, 140, 60, 255), width=4)
draw.line((128, 28, 128, 228), fill=(0, 180, 80, 255), width=6)
draw.line((28, 128, 228, 128), fill=(0, 180, 80, 255), width=6)
draw.polygon([(128, 44), (92, 164), (128, 140), (164, 164)], fill=(0, 255, 102, 255))
draw.ellipse((114, 114, 142, 142), fill=(255, 60, 60, 255))
img.save(ico_path, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])

# 4. Trova SimConnect.dll
sc_dir = os.path.dirname(SimConnect.__file__)
dll_path = os.path.join(sc_dir, "SimConnect.dll")

# 5. Compila da zero con PyInstaller
cmd = [
    sys.executable, "-m", "PyInstaller",
    "--noconsole",
    "--onefile",
    f"--icon={ico_path}",
    f"--add-data={ico_path}{os.pathsep}.",
    "--name=MB339-Nav-Flightplan",
    "--clean",
    "--noconfirm"
]

if os.path.exists(dll_path):
    cmd.append(f"--add-binary={dll_path}{os.pathsep}SimConnect")
    cmd.append(f"--add-data={dll_path}{os.pathsep}SimConnect")

cmd.append(main_path)

print("Compilazione pulita in corso...")
subprocess.check_call(cmd)
print("\nCOMPILAZIONE COMPLETATA! Nuovo file creato in:", os.path.join(dist_dir, "MB339-Nav-Flightplan.exe"))