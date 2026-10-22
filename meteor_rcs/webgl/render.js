// Exact HDF5 gallery arrays / numerically solved isodensity. Only camera moves.
import init,{MeshView} from './pkg/rustplotlib_web.js';
await init();
const scenes=await(await fetch('scenes.json',{cache:'no-store'})).json();
const glyph={};
await Promise.all(['axz','axr','axx','axy','log','iso','density'].map(name=>new Promise((resolve,reject)=>{
 const im=new Image();im.onload=()=>{glyph[name]=im;resolve()};im.onerror=reject;im.src='glyphs/'+name+'.svg';
})));

const gpu=document.querySelector('#gpu'),out=document.querySelector('#output'),ctx=out.getContext('2d');
const view=new MeshView(gpu),mode=document.querySelector('#mode'),status=document.querySelector('#status');
const colors={blue:[.14,.34,.46],green:[.15,.45,.41],purple:[.5,.27,.57]};
let current,progress=0,running=false;
const line=(a,b,c)=>[...a,...c,...b,...c];
function axes(which){
 let s=[];
 if(which==='height'){
  s.push(...line([-5,-10,-3],[20,-10,-3],colors.blue),...line([-5,-10,-3],[-5,10,-3],colors.green),...line([-5,-10,-3],[-5,-10,2.7],colors.purple));
  for(let x=-5;x<=20;x+=5)s.push(...line([x,-10,-3],[x,-9.6,-3],colors.blue));
  for(let y=-10;y<=10;y+=5)s.push(...line([-5,y,-3],[-4.6,y,-3],colors.green));
 }else{s.push(...line([-2,0,0],[8,0,0],colors.blue),...line([0,0,0],[0,4.5,0],colors.green),...line([0,0,0],[0,0,4.5],colors.purple));}
 return new Float32Array(s);
}
function load(){
 current=scenes[mode.value];view.set_axis_scale(...current.scale);
 if(current.rgb)view.set_colored_mesh(new Float32Array(current.xyz),new Uint32Array(current.triangles),new Float32Array(current.rgb));
 else{view.set_mesh(new Float32Array(current.xyz),new Uint32Array(current.triangles),new Float32Array(current.values));view.set_colormap(new Float32Array(current.palette));view.set_scale(...current.colorRange);}
 view.set_bounds(...current.bounds);view.set_lines(new Float32Array([...axes(mode.value),...(current.seams||[])]));progress=0;draw(0);status.textContent='Ready';
}
function text(t,x,y,size=30,color='#172333'){ctx.font=size+'px Georgia,serif';ctx.fillStyle=color;ctx.fillText(t,x,y);}
function math(name,x,y,h=38){const im=glyph[name];ctx.drawImage(im,x,y-h,h*im.naturalWidth/im.naturalHeight,h);}
function rule(y,c){ctx.strokeStyle=c;ctx.lineWidth=5;ctx.beginPath();ctx.moveTo(1560,y);ctx.lineTo(1608,y);ctx.stroke();}
function draw(t){
 const q=t*(current.cameraTargets.length-1),i=Math.min(current.cameraTargets.length-2,Math.floor(q)),u=q-i;
 const target=current.cameraTargets[i].map((v,k)=>v+(current.cameraTargets[i+1][k]-v)*u);
 const half=[0,1,2].map(k=>(current.bounds[2*k+1]-current.bounds[2*k])/2);
 view.set_bounds(target[0]-half[0],target[0]+half[0],target[1]-half[1],target[1]+half[1],target[2]-half[2],target[2]+half[2]);
 view.set_camera((mode.value==='height'?-.85:.85)+2*Math.PI*t,mode.value==='height'?.42:.28,current.cameraDistance);
 ctx.fillStyle='white';ctx.fillRect(0,0,1920,900);ctx.drawImage(gpu,0,0);
 if(mode.value==='height'){
  text('A density graph',1560,130,32);
  rule(200,'#245774');math('axz',1630,212,38);text('−5 to 20; +z behind',1560,255,24);
  rule(320,'#267369');math('axr',1630,332,38);text('−10 to 10; signed slice',1560,375,24);
  rule(440,'#804592');text('Log density',1630,450,30);text('height and colour:',1560,495,25);math('log',1560,542,36);
  const grad=ctx.createLinearGradient(0,810,0,620),pal=current.palette;
  for(let i=0;i<pal.length/3;i++)grad.addColorStop(i/(pal.length/3-1),'rgb('+pal[3*i]*255+','+pal[3*i+1]*255+','+pal[3*i+2]*255+')');
  ctx.fillStyle=grad;ctx.fillRect(1570,620,35,190);text('4',1625,635,27);text('−3',1625,810,27);
  text('Height is density,',1560,850,25);text('not physical distance.',1560,884,25);
 }else{
  text('Outer density level',1560,75,29);math('iso',1560,130,36);
  text('Cut faces: density',1560,193,29);math('density',1560,247,38);
  const top=292,bottom=527,grad=ctx.createLinearGradient(0,bottom,0,top),pal=current.cutPalette;
  for(let i=0;i<pal.length/3;i++)grad.addColorStop(i/(pal.length/3-1),'rgb('+pal[3*i]*255+','+pal[3*i+1]*255+','+pal[3*i+2]*255+')');
  ctx.fillStyle=grad;ctx.fillRect(1570,top,32,bottom-top);
  const [lo,hi]=current.cutRange;
  for(const value of [.05,.1,1,10]){
   const y=bottom-(bottom-top)*Math.log(value/lo)/Math.log(hi/lo);
   text(value===hi?'≥10':String(value),1620,y+8,26);
  }
  text('Logarithmic scale',1560,570,25);
  rule(622,'#245774');math('axz',1630,634,35);
  rule(685,'#267369');math('axx',1630,697,35);
  rule(748,'#804592');math('axy',1630,760,35);
  text('Same spatial scale',1560,812,25);
  text('Gold: enlarged grain',1560,857,24);
  text('Plasma extends outside.',1560,891,24);
 }
}
async function orbit(record=false){
 if(running)return;running=true;
 const chunks=[],supported=['video/mp4;codecs=avc1.640028','video/mp4','video/webm;codecs=vp9','video/webm'].find(MediaRecorder.isTypeSupported);
 let recorder;
 if(record){
  recorder=new MediaRecorder(out.captureStream(30),{mimeType:supported,videoBitsPerSecond:14000000});
  recorder.ondataavailable=e=>{if(e.data.size)chunks.push(e.data)};
  recorder.onstop=async()=>{const link=document.querySelector('#download');link.href=URL.createObjectURL(new Blob(chunks,{type:recorder.mimeType}));link.download='do_'+mode.value+'.'+(recorder.mimeType.includes('mp4')?'mp4':'webm');link.hidden=false;const saved=await fetch('/record/'+link.download,{method:'POST',body:new Blob(chunks,{type:recorder.mimeType})});status.textContent=saved.ok?'Recording saved':'Recording save failed';};
  document.querySelector('#download').hidden=true;recorder.start();
 }
 const start=performance.now(),duration=12000;
 await new Promise(resolve=>{function frame(now){progress=Math.min(1,(now-start)/duration);draw(progress);status.textContent=(record?'Recording ':'Orbit ')+Math.round(progress*100)+'%';if(progress<1)requestAnimationFrame(frame);else resolve();}requestAnimationFrame(frame)});
 if(recorder)recorder.stop();running=false;if(!record)status.textContent='Orbit complete';
}
document.querySelector('#record').onclick=()=>orbit(true);document.querySelector('#preview').onclick=()=>orbit(false);
document.querySelector('#reset').onclick=()=>{if(!running){draw(0);status.textContent='Ready'}};
mode.onchange=()=>{if(!running)load()};
document.querySelector('#depth').onclick=()=>{
 if(running)return;const gl=gpu.getContext('webgl2');
 const test=(reverse=false)=>{
  const pos=[-.8,-.8,0,.8,-.8,0,0,.8,0,-.8,-.8,.5,.8,-.8,.5,0,.8,.5],idx=reverse?[3,4,5,0,1,2]:[0,1,2,3,4,5];
  view.set_colored_mesh(new Float32Array(pos),new Uint32Array(idx),new Float32Array([1,0,0,1,0,0,1,0,0,0,1,0,0,1,0,0,1,0]));
  view.set_lines(new Float32Array());view.set_axis_scale(1,1,1);view.set_bounds(-1,1,-1,1,-1,1);view.set_camera(0,1.5,2.8);view.draw();
  const p=new Uint8Array(4);gl.readPixels(768,450,1,1,gl.RGBA,gl.UNSIGNED_BYTE,p);return [...p];
 };
 const a=test(),b=test(true),pass=a[1]>a[0]&&a.every((v,i)=>v===b[i])&&gl.getError()===gl.NO_ERROR;
 load();status.textContent='Depth test '+(pass?'PASS':'FAIL')+': '+JSON.stringify(a)+' / '+JSON.stringify(b);
};
load();
