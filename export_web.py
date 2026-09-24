"""Export browser decks with content-addressed media and endpoint validation."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import cv2
import numpy as np
from PIL import Image, ImageDraw

DECKS = {
    "PlanckToKTB": ("planck-to-ktb", "Planck law to radio noise"),
    "FriisVoyager": ("friis-voyager", "Friis transmission and Voyager"),
    "TelecomModulations": ("telecom-modulations", "Digital modulation"),
}


def export(scene, root):
    slug, title = DECKS[scene]
    dest = root / slug
    dest.mkdir(parents=True, exist_ok=True)
    frames = []
    for number, slide in enumerate(json.loads(Path(f"slides/{scene}.json").read_text())["slides"], 1):
        cap = cv2.VideoCapture(slide["file"])
        cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 2))
        ok, frame = cap.read()
        cap.release()
        if not ok:
            raise RuntimeError(f"Unreadable slide: {scene} {number}")
        fraction = (np.max(np.abs(frame.astype(np.int16) - [31, 17, 7]), axis=2) > 18).mean()
        if fraction < 0.01:
            raise RuntimeError(f"Blank slide ending: {scene} {number}")
        picture = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        picture.save(dest / f"qa-{number:02d}.png")
        picture.thumbnail((640, 360))
        frames.append(picture)
    contact = Image.new("RGB", (1280, ((len(frames) + 1) // 2) * 388), "#253040")
    draw = ImageDraw.Draw(contact)
    for i, frame in enumerate(frames):
        x, y = (i % 2) * 640, (i // 2) * 388
        contact.paste(frame, (x, y))
        draw.text((x + 10, y + 365), f"Slide {i + 1}", fill="white")
    contact.save(dest / "qa-contact.jpg")
    subprocess.run(["manim-slides", "convert", "--folder", "slides", "--offline", scene, str(dest / "index.html")], check=True)
    page = (dest / "index.html").read_text().replace("<title>Manim Slides</title>", f"<title>{title}</title>")
    for media in (dest / "index_assets").glob("*.mp4"):
        new_name = hashlib.sha256(media.read_bytes()).hexdigest()[:20] + ".mp4"
        page = page.replace("index_assets/" + media.name, "index_assets/" + new_name)
        media.rename(media.with_name(new_name))
    guard = Path("final_slide_guard.js").read_bytes()
    guard_name = "navigation-" + hashlib.sha256(guard).hexdigest()[:12] + ".js"
    (dest / "index_assets" / guard_name).write_bytes(guard)
    page = page.replace("</body>", f'<script src="index_assets/{guard_name}"></script>\n</body>')
    (dest / "index.html").write_text(page)
    print(f"{scene}: {len(frames)} nonblank slide endings; exported to {dest}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("scenes", nargs="+", choices=list(DECKS))
    args = parser.parse_args()
    for scene in args.scenes:
        export(scene, args.output)
