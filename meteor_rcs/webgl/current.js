// Real, staggered Yee samples from the archived Rust solver; no sinusoidal synthesis.
import init,{FieldView} from './pkg/rustplotlib_web.js';
await init();
const glyph={};
await Promise.all(['electric','current'].map(name=>new Promise((resolve,reject)=>{
 const im=new Image();im.onload=()=>{glyph[name]=im;resolve()};im.onerror=reject;im.src='glyphs/'+name+'.svg';
})));

const d=await(await fetch('current.json')).json(),n=d.n,len=n*n;
const e=document.querySelector('#electric'),j=document.querySelector('#current');
const ev=new FieldView(e),jv=new FieldView(j),out=document.querySelector('#output'),c=out.getContext('2d');
const status=document.querySelector('#status');
const movie=document.createElement('canvas');movie.width=1920;movie.height=900;const mc=movie.getContext('2d');
const ee=new Float32Array(d.e),jj=new Float32Array(d.j);
ev.set_data(n,n,ee.subarray(0,len));jv.set_data(n,n,jj.subarray(0,len));
ev.set_scale(-d.escale,d.escale,0,1,0);jv.set_scale(-d.jscale,d.jscale,2,d.jscale/1000,0);jv.set_view(.3515625,.34375,.6640625,.65625);
function text(t,x,y,size=30){c.fillStyle='#172333';c.font=size+'px Georgia,serif';c.fillText(t,x,y);}
function draw(frame){
 ev.set_data(n,n,ee.subarray(frame*len,(frame+1)*len));jv.set_data(n,n,jj.subarray(frame*len,(frame+1)*len));
 c.fillStyle='white';c.fillRect(0,0,1920,1040);
 for(const [canvas,x,title] of [[e,150,'Total E_z [V/m]'],[j,1050,'Electron current J_z [A/m²]']]){
  c.drawImage(canvas,x,105);c.strokeStyle='#596779';c.lineWidth=2;c.strokeRect(x,105,704,704);
  text(x===150?'Total electric field':'Electron current',x+20,40,30);
  const im=glyph[x===150?'electric':'current'];c.drawImage(im,x+380,12,36*im.naturalWidth/im.naturalHeight,36);
  const ticks=x===150?[-1.5,-1,-.5,0,.5,1,1.5]:[-.5,-.25,0,.25,.5];
  const xmin=x===150?-1.625:-.5,zmin=x===150?-1.6:-.5,span=x===150?3.2:1.;
  for(const value of ticks){
   const px=(value-xmin)/span*704,pz=(value-zmin)/span*704;
   text(''+value,x+px-13,850,25);text(''+value,x-65,815-pz,25);
  }
  if(x===150){c.strokeStyle='#596779';c.setLineDash([8,8]);c.strokeRect(x+1.125/3.2*704,105+1.1/3.2*704,704/3.2,704/3.2);c.setLineDash([]);}
  text('x [m]: incident wave →',x+175,900,30);
  c.save();c.translate(x-95,565);c.rotate(-Math.PI/2);text('z [m]: trajectory axis',0,0,29);c.restore();
 }
 text('53.5 MHz; incident peak 1 V/m; frozen plasma density',150,965,30);
 text('Time: '+d.times[frame].toFixed(1)+' ns',1050,965,32);
 text('Blue: negative; red: positive. Dashed box: current-panel zoom. Current uses a signed asinh scale.',150,1020,25);
 // The current plot has the full same range on every frame.
 text('±'+d.jscale.toExponential(2)+' A/m²; signed asinh',1120,85,24);
 text('±'+d.escale.toFixed(2)+' V/m; linear',300,85,24);
 mc.fillStyle='white';mc.fillRect(0,0,1920,900);const width=1920*900/1040;mc.drawImage(out,(1920-width)/2,0,width,900);
}
let busy=false;
async function run(record){
 if(busy)return;busy=true;const chunks=[];
 let recorder;
 if(record){
  const mime=['video/mp4;codecs=avc1.640028','video/mp4','video/webm;codecs=vp9'].find(MediaRecorder.isTypeSupported);
  recorder=new MediaRecorder(movie.captureStream(30),{mimeType:mime,videoBitsPerSecond:14000000});
  recorder.ondataavailable=e=>{if(e.data.size)chunks.push(e.data)};
  recorder.onstop=async()=>{
   const name='fdtd_current.'+(recorder.mimeType.includes('mp4')?'mp4':'webm');
   const r=await fetch('/record/'+name,{method:'POST',body:new Blob(chunks,{type:recorder.mimeType})});
   status.textContent=r.ok?'Current movie saved':'Save failed';
  };
  recorder.start();
 }
 const start=performance.now();
 await new Promise(resolve=>{
  function frame(now){const t=Math.min(1,(now-start)/14000),i=Math.min(d.times.length-1,Math.round(t*(d.times.length-1)));draw(i);status.textContent='Time '+d.times[i].toFixed(1)+' ns';if(t<1)requestAnimationFrame(frame);else resolve();}
  requestAnimationFrame(frame);
 });
 const peak=d.peakFrame;status.textContent='Peak-current snapshot: '+d.times[peak].toFixed(1)+' ns';
 await new Promise(resolve=>{const start=performance.now();function hold(now){draw(peak);if(now-start<1000)requestAnimationFrame(hold);else resolve();}requestAnimationFrame(hold);});if(recorder)recorder.stop();busy=false;
}
document.querySelector('#record').onclick=()=>run(true);document.querySelector('#play').onclick=()=>run(false);
draw(0);status.textContent='Ready';
