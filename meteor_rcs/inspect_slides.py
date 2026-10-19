"""Decode the actual last frame of every exported slide and make review sheets."""
from pathlib import Path
import json

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageColor


def main():
    root=Path(__file__).resolve().parents[1]
    config=json.loads((root/'slides/MeteorHeadRCS.json').read_text())
    slides=config['slides']
    background_bgr=list(ImageColor.getrgb(config['background_color']))[::-1]
    output=root/'web/meteor-head-rcs/review'
    output.mkdir(parents=True,exist_ok=True)
    thumbs=[]
    for i,slide in enumerate(slides,1):
        capture=cv2.VideoCapture(str(root/slide['file']))
        n=int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        capture.set(cv2.CAP_PROP_POS_FRAMES,n-1)
        ok,frame=capture.read();capture.release()
        if not ok:raise RuntimeError(f'Cannot decode final frame of slide {i}')
        contrast=(np.max(abs(frame.astype(float)-background_bgr),axis=2)>25).mean()
        if contrast<.01:raise RuntimeError(f'Blank final frame in slide {i}')
        picture=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
        picture.save(output/f'slide-{i:02d}.png')
        picture.thumbnail((640,360));thumbs.append(picture)
    for page in range((len(thumbs)+7)//8):
        sheet=Image.new('RGB',(1280,4*390),'#253040');draw=ImageDraw.Draw(sheet)
        for j,picture in enumerate(thumbs[page*8:page*8+8]):
            x=(j%2)*640;y=(j//2)*390
            sheet.paste(picture,(x,y));draw.text((x+10,y+365),f'Slide {page*8+j+1}',fill='white')
        sheet.save(output/f'contact-{page+1}.jpg')
    print(f'Decoded and checked all {len(slides)} final frames: {output}')


if __name__=='__main__':main()
