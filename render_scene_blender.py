import argparse
from math import radians
from pathlib import Path
import sys

import numpy as np

import bpy
import bmesh
import mathutils

argv = sys.argv
if "--" not in argv:
    argv = []
else:
    argv = argv[argv.index("--") + 1:]

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
parser.add_argument("--nframes", type=int, required=True)
opt = parser.parse_args(argv)

root_path = Path(opt.output_path)
root_path.mkdir(parents=True, exist_ok=True)

ctx = bpy.context
camera = ctx.scene.camera

def pose2mat(pose):
    mat = np.eye(4)
    mat[:3, :] = pose[:15].reshape(3, 5)[:, :4]
    return mat

all_payloads = []
for idx in range(opt.nframes):
    # Set rotation matrix
    angle = np.pi * 2 * idx / opt.nframes
    # angle=0
    rotation_matrix = mathutils.Matrix.Rotation(angle, 4, "Y")
    translation = mathutils.Vector((0.15 * np.sin(-angle), 0.0, 0.15 * np.cos(-angle)))
    translation_matrix = mathutils.Matrix.Translation(translation)
    matrix = translation_matrix @ rotation_matrix

    # Change the configurations
    ctx.scene.render.resolution_y = 200
    ctx.scene.render.resolution_x = 200
    camera.data.sensor_height = 1
    camera.data.sensor_width = 1
    camera.data.clip_start = 0.1
    camera.data.clip_end = 100
    camera.data.angle = radians(110)

    # Store payload
    to_emit_mat = np.linalg.inv(np.array(matrix))

    payload = np.linalg.inv(np.array(matrix))[:3, :]
    payload = np.concatenate([
        payload,
        np.array([
            [ctx.scene.render.resolution_y],
            [ctx.scene.render.resolution_x],
            [camera.data.lens / camera.data.sensor_height * ctx.scene.render.resolution_y],
        ]),
    ], axis=-1)
    payload = payload.flatten()
    payload = np.concatenate([
        payload,
        np.array([camera.data.clip_start, camera.data.clip_end]),
    ])
    all_payloads.append(payload)

    # Configure scene
    camera.rotation_euler = matrix.to_euler("XYZ")
    # camera.rotation_euler = mathutils.Vector((radians(0), radians(0), 0))
    camera.location = translation
    ctx.scene.render.image_settings.file_format = "PNG"
    ctx.scene.render.filepath = str(root_path / ("img%02d.png" % idx))
    bpy.ops.render.render(write_still = 1)

all_payloads = np.stack(all_payloads)
np.save(root_path / "poses_bounds.npy", all_payloads)
