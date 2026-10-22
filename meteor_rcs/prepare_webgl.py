"""Exact HDF5 DO arrays to a Rustplotlib GPU scene; comments retain provenance."""
from pathlib import Path
import json, shutil, subprocess
import h5py
import numpy as np
ROOT=Path(__file__).resolve().parent
def build(package=None):
    target=ROOT/'webgl'; target.mkdir(exist_ok=True)
    if package:
        dest=target/'pkg';dest.mkdir(exist_ok=True)
        for name in ['rustplotlib_web.js','rustplotlib_web_bg.wasm']:
            shutil.copy2(Path(package)/name,dest/name)
    with h5py.File(ROOT/'data.h5') as f:
        x=f['gallery/z'][:];y=f['gallery/r'][:]
        h=f['gallery/log_density'][:].reshape(len(y),len(x))
        theta=f['gallery/theta'][:];radius=f['gallery/radius'][:]
    xx,yy=np.meshgrid(x,y);ok=np.isfinite(h).ravel()
    remap=np.full(ok.size,-1);remap[ok]=np.arange(sum(ok));faces=[]
    for j in range(len(y)-1):
        for i in range(len(x)-1):
            a=j*len(x)+i;b=a+1;c=a+len(x);d=c+1
            for t in [(a,b,c),(b,d,c)]:
                if all(ok[list(t)]):faces.append(remap[list(t)].tolist())
    palette=np.frombuffer((ROOT/'plots/src/support/dimant_colormap.rgb').read_bytes(),dtype=np.uint8)/255
    scenes={'height':dict(xyz=np.c_[xx.ravel()[ok],yy.ravel()[ok],h.ravel()[ok]].ravel().tolist(),
        triangles=np.ravel(faces).tolist(),values=h.ravel()[ok].tolist(),
        bounds=[-5,20,-10,10,-3,4],scale=[1,1,2.5],colorRange=[-3,4],palette=palette.tolist())}
    phi=np.linspace(0,2*np.pi,129);xyz=[];tri=[];rgb=[]
    for r,t in zip(radius,theta):
        for p in phi:
            xyz.append([r*np.cos(t),r*np.sin(t)*np.cos(p),r*np.sin(t)*np.sin(p)])
            rgb.append([.19,.51,.48])
    for j in range(len(theta)-1):
        for i in range(len(phi)-1):
            if 0<=phi[i]<np.pi/2:continue
            a=j*len(phi)+i;b=a+1;c=a+len(phi);d=c+1;tri.extend([(a,b,c),(b,d,c)])
    # Enlarged spherical origin marker, occluded by the actual surface where appropriate.
    off=len(xyz);nt=17;np_=33
    for t in np.linspace(0,np.pi,nt):
        for p in np.linspace(0,2*np.pi,np_):
            xyz.append([.17*np.cos(t),.17*np.sin(t)*np.cos(p),.17*np.sin(t)*np.sin(p)])
            rgb.append([.68,.34,.12])
    for j in range(nt-1):
        for i in range(np_-1):
            a=off+j*np_+i;b=a+1;c=a+np_;d=c+1;tri.extend([(a,b,c),(b,d,c)])
    scenes['physical']=dict(xyz=np.ravel(xyz).tolist(),triangles=np.ravel(tri).tolist(),
        rgb=np.ravel(rgb).tolist(),bounds=[-2,8,-5,5,-5,5],scale=[1,1,1])
    # Fit the real perspective camera around the mesh, allowing a small target
    # pan to keep its projected bounding box centred. Geometry never changes.
    for kind,scene in scenes.items():
        bounds=np.array(scene['bounds']).reshape(3,2);scale=np.array(scene['scale'])
        centre=bounds.mean(axis=1);span=np.diff(bounds).ravel()
        radius=np.linalg.norm(span*scale)/2
        xyz=np.array(scene['xyz']).reshape(-1,3)
        if kind=='height':
            xyz=np.vstack([xyz,[[-5,-10,-3],[20,-10,-3],[-5,10,-3],[-5,-10,2.7]]])
        else:
            xyz=np.vstack([xyz,[[-2,0,0],[8,0,0],[0,4.5,0],[0,0,4.5]]])
        points=(xyz-centre)*scale/radius
        pitch=.42 if kind=='height' else .28
        yaws=np.linspace(-.85 if kind=='height' else .85,
                         (-.85 if kind=='height' else .85)+2*np.pi,181)
        def frame(yaw,distance):
            front=np.array([np.cos(yaw)*np.cos(pitch),np.sin(yaw)*np.cos(pitch),np.sin(pitch)])
            right=np.array([-np.sin(yaw),np.cos(yaw),0]);up=np.cross(front,right)
            z=distance-points@front
            base=np.c_[points@right,points@up];shift=np.zeros(2)
            for _ in range(5):
                projected=(base-shift)/z[:,None]*2.414
                mid=(projected.min(axis=0)+projected.max(axis=0))/2
                shift+=mid*distance/2.414
            projected=(base-shift)/z[:,None]*2.414
            width,height=np.ptp(projected,axis=0)
            target=centre+(right*shift[0]+up*shift[1])*radius/scale
            return max(width/(1536/900)/1.82,height/1.72),target
        distances=[]
        for yaw in yaws:
            low,high=1.25,4.
            for _ in range(16):
                mid=(low+high)/2
                if frame(yaw,mid)[0]>1:low=mid
                else:high=mid
            distances.append(high)
        distance=float(max(distances)+.05)
        scene['cameraDistance']=distance
        scene['cameraTargets']=[frame(yaw,distance)[1].tolist() for yaw in yaws]
        print('Fitted camera',kind,distance)
    (target/'scenes.json').write_text(json.dumps(scenes,separators=(',',':'),allow_nan=False))
    subprocess.run(['cargo','run','--quiet','--release','--manifest-path',str(ROOT/'plots/Cargo.toml'),
                    '--','--check-webgl-layout',str(target/'scenes.json')],check=True)
    current=ROOT/'current_preview.h5'
    if current.exists():
        with h5py.File(current) as f:
            e=f['electric_z_v_m'][:];j=f['current_z_a_m2'][:]
            data=dict(n=e.shape[1],axis=f['axis_x_m'][:].tolist(),times=(f['time_e_s'][:]*1e9).tolist(),
                j=j.transpose(0,2,1).ravel().tolist(),e=e.transpose(0,2,1).ravel().tolist(),
                jscale=float(np.max(abs(j))),escale=float(np.max(abs(e))),
                peakFrame=int(np.argmax(np.max(abs(j),axis=(1,2)))))
        (target/'current.json').write_text(json.dumps(data,separators=(',',':'),allow_nan=False))
    print('Exact WebGL meshes:',len(faces),'height triangles;',len(tri),'spatial triangles')
if __name__=='__main__':
    import sys
    build(sys.argv[1] if len(sys.argv)>1 else None)
