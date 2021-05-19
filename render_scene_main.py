from pathlib import Path
import subprocess


BLENDER = "blender"
SCENE_PATH = Path("/home/budmonde/Documents/0_classroom/classroom.blend")
subprocess.run([
    BLENDER,
        "--background", SCENE_PATH,
        "--python", "render_scene_blender.py",
        "--",
            "--output_path", "./classroom/",
            "--nframes", "16",
],
check=True)
