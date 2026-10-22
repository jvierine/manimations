"""Conservative per-frame bounds for the isotropic-direction movie."""
from pathlib import Path
import json
import subprocess
import tempfile

import numpy as np

ROOT = Path(__file__).resolve().parent


def main():
    # All dots and cone vertices are inside this sphere. Its 0.03 margin
    # covers glyph radii and the gap between adjacent angular samples.
    z = np.linspace(-1, 1, 181)
    phi = np.linspace(0, 2 * np.pi, 361)
    points = np.array([
        [1.35 * np.sqrt(1 - s * s) * np.cos(p),
         1.35 * np.sqrt(1 - s * s) * np.sin(p), 1.35 * s]
        for s in z for p in phi
    ])
    scene = dict(
        xyz=points.ravel().tolist(), bounds=[-1.4, 1.4] * 3, scale=[1, 1, 1],
        cameraDistance=1.58, cameraTargets=[[0, 0, 0], [0, 0, 0]],
        yawStart=-.55, yawSpan=1.4, pitch=.22, viewWidth=120.,
        gutterLeft=128., frames=480,
    )
    # Temporary JSON is browser-layout transport, not a scientific data product.
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'layout.json'
        path.write_text(json.dumps({'ionization': scene}))
        subprocess.run([
            'cargo', 'run', '--quiet', '--release', '--manifest-path',
            str(ROOT / 'plots/Cargo.toml'), '--', '--check-webgl-layout', str(path),
        ], check=True)


if __name__ == '__main__':
    main()
