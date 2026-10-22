// A velocity-direction illustration, not a plasma-density or collision simulation.
// DO Part 2 assumes angle-independent G_ion at fixed relative speed. The frame
// here is the collision centre of mass, not the atmosphere or grain frame.
import init,{MeshView} from './pkg/rustplotlib_web.js';
await init();
const gpu=document.querySelector('#gpu'),out=document.querySelector('#output'),ctx=out.getContext('2d');
const view=new MeshView(gpu),status=document.querySelector('#status');
const red=[.70,.20,.18],blue=[.14,.34,.46],green=[.15,.45,.41],grey=[.45,.48,.52];
const dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0);
const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
const unit=a=>a.map(v=>v/Math.hypot(...a));
const directions=[];
// Equal-area Fibonacci samples with antipodal partners: no net beam direction.
for(let i=0;i<128;i++){
 const z=(i+.5)/128,phi=i*Math.PI*(3-Math.sqrt(5)),r=Math.sqrt(1-z*z);
 const d=[r*Math.cos(phi),r*Math.sin(phi),z];directions.push(d,d.map(v=>-v));
}
const a=unit([.8,-.6,.25]),b=unit([-.45,.25,.86]),halfAngle=Math.PI/6;
const oct=[[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]];
const faces=[0,2,4,2,1,4,1,3,4,3,0,4,2,0,5,1,2,5,3,1,5,0,3,5];
const segment=(p,q,c)=>[...p,...c,...q,...c];
function cone(axis,color,amount){
 const u=unit(cross(axis,[0,0,1])),v=cross(axis,u),ring=[];let lines=[];
 for(let i=0;i<=64;i++){
  const phi=2*Math.PI*i/64;
  ring.push(axis.map((x,k)=>1.32*amount*(x*Math.cos(halfAngle)+(u[k]*Math.cos(phi)+v[k]*Math.sin(phi))*Math.sin(halfAngle))));
  if(i)lines.push(...segment(ring[i-1],ring[i],color));
  if(i%16===0)lines.push(...segment([0,0,0],ring[i],color));
 }
 return lines;
}
function text(value,x,y,size=36,color='#172333'){
 ctx.font=size+'px Georgia,serif';ctx.fillStyle=color;ctx.fillText(value,x,y);
}
function draw(t){
 const seconds=16*t,coneAmount=Math.max(0,Math.min(1,(seconds-7)/1.5));
 let xyz=[],rgb=[],tri=[];
 function particle(p,r,c){const offset=xyz.length/3;for(const d of oct){xyz.push(...p.map((x,k)=>x+r*d[k]));rgb.push(...c)}tri.push(...faces.map(i=>i+offset));}
 particle([0,0,0],.055,grey);
 for(let i=0;i<directions.length;i++){
  const birth=4*((i*73)%256)/256;
  if(seconds<birth)continue;
  const d=directions[i],radius=1.10*Math.min(1,Math.max(0,(seconds-birth)/1.4));
  const color=coneAmount>.9?(dot(d,a)>Math.cos(halfAngle)?blue:dot(d,b)>Math.cos(halfAngle)?green:red):red;
  particle(d.map(x=>x*radius),.027,color);
 }
 view.set_colored_mesh(new Float32Array(xyz),new Uint32Array(tri),new Float32Array(rgb));
 view.set_axis_scale(1,1,1);view.set_bounds(-1.4,1.4,-1.4,1.4,-1.4,1.4);
 const lines=[...cone(a,blue,coneAmount),...cone(b,green,coneAmount)];
 view.set_lines(new Float32Array(lines));view.set_camera(-.55+1.4*Math.min(1,t/.8),.22,1.58);
 ctx.fillStyle='white';ctx.fillRect(0,0,1920,900);ctx.drawImage(gpu,0,0);
 text('Collision centre-of-mass',1280,75,36,'#245774');
 text('frame',1280,123,36,'#245774');
 text('Many separate collisions',1280,215,39);
 text('One dot = one ion outcome',1280,270,33,'#b33c3c');
 text('No preferred outgoing direction',1280,360,36);
 text('No ion beam imposed at birth',1280,415,34);
 if(coneAmount>0){
  ctx.fillStyle='#245774';ctx.fillRect(1280,486,47,7);text('Cone A',1350,500,36,'#245774');
  ctx.fillStyle='#267369';ctx.fillRect(1280,551,47,7);text('Cone B',1350,565,36,'#267369');
  text('Equal solid angles',1280,650,38);
  text('Equal expected shares',1280,712,38);
 }
 text('Centre: ionizing encounter',1280,816,30,'#596779');
 text('Fixed collision speed',1280,866,30,'#596779');
}
let running=false;draw(.001);status.textContent='Ready';
async function play(record){
 if(running)return;running=true;const chunks=[];
 const mime=['video/mp4;codecs=avc1.640028','video/mp4','video/webm;codecs=vp9'].find(MediaRecorder.isTypeSupported);
 let recorder;
 if(record){
  recorder=new MediaRecorder(out.captureStream(30),{mimeType:mime,videoBitsPerSecond:12000000});
  recorder.ondataavailable=e=>{if(e.data.size)chunks.push(e.data)};
  recorder.onstop=async()=>{
   const blob=new Blob(chunks,{type:recorder.mimeType}),ext=recorder.mimeType.includes('mp4')?'mp4':'webm';
   const link=document.querySelector('#download');link.href=URL.createObjectURL(blob);link.download='g_ion.'+ext;link.hidden=false;
   const result=await fetch('/record/'+link.download,{method:'POST',body:blob});status.textContent=result.ok?'Recording saved':'Save failed';
  };recorder.start();
 }
 const start=performance.now();
 await new Promise(resolve=>{function step(now){const t=Math.min(1,(now-start)/16000);draw(t);status.textContent='Explaining '+Math.round(100*t)+'%';if(t<1)requestAnimationFrame(step);else resolve()}requestAnimationFrame(step)});
 if(recorder)recorder.stop();else status.textContent='Explanation complete';running=false;
}
document.querySelector('#preview').onclick=()=>play(false);document.querySelector('#record').onclick=()=>play(true);
