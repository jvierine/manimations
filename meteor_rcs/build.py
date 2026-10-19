"""Render, export and inspect the complete meteor deck; no scientific jobs."""
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def main():
    commands=[
        [sys.executable,'-m','meteor_rcs.prepare_assets'],
        ['manim-slides','render','-r','1920,1080','--fps','30','--disable_caching',
         '-o','MeteorHeadRCS','meteor_head_rcs.py','MeteorHeadRCS'],
        [sys.executable,'export_web.py','web','MeteorHeadRCS'],
        [sys.executable,'-m','meteor_rcs.inspect_slides'],
    ]
    for command in commands:
        subprocess.run(command,cwd=ROOT,check=True)
    package()


def package():
    destination=ROOT/'web/meteor-head-rcs'
    names=['AGENTS.md','meteor_head_rcs.py','test_meteor_rcs.py','meteor_rcs/README.md',
           'meteor_rcs/inputs.h5','meteor_rcs/data.h5','meteor_rcs/prepare_assets.py',
           'meteor_rcs/do_density.py','meteor_rcs/__init__.py','meteor_rcs/build.py',
           'meteor_rcs/inspect_slides.py','planck_to_ktb.py','rayleigh_jeans_accuracy.py',
           'export_web.py','final_slide_guard.js','manim.cfg']
    names += ['meteor_rcs/plots/Cargo.toml','meteor_rcs/plots/Cargo.lock',
              'meteor_rcs/plots/src/main.rs']
    names += [str(p.relative_to(ROOT)) for p in (ROOT/'meteor_rcs/assets').glob('*')]
    with zipfile.ZipFile(destination/'source.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for name in names:archive.write(ROOT/name,arcname=name)
    print('Complete browser deck:',destination/'index.html')


if __name__=='__main__':main()
