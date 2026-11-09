/** Render a small editable scientific scene. Units in the input are points.
 * Usage: node compile_pptx.mjs scene.json build-directory
 * Resolve @oai/artifact-tool and skia-canvas through the host's supplied modules.
 * This creates a draft and previews; the host must finalize and inspect them.
 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {Presentation, PresentationFile} from '@oai/artifact-tool';
import {createRequire} from 'node:module';
const runtimeRequire=createRequire(import.meta.resolve('@oai/artifact-tool'));
const {FontLibrary}=runtimeRequire('skia-canvas');
const PX=4/3;
const here=path.dirname(fileURLToPath(import.meta.url));
const asPx=x=>x*PX;
const pos=e=>({left:asPx(e.x),top:asPx(e.y),width:asPx(e.w),height:asPx(e.h)});
const assert=(ok,msg)=>{if(!ok)throw new Error(msg);};
const fillValue=v=>(v===null||v===''||v==='none')?'none':v;
const fields=(obj,keys)=>{for(const k of Object.keys(obj))assert(keys.includes(k),`Unsupported field ${k}`);};
const boxKeys=['id','type','x','y','w','h'];
const styleKeys=['fontFamily','fontSize','color','bold','italic','align','verticalAlign','lineSpacing'];
function rect(e,W,H){
 for(const k of ['x','y','w','h'])assert(Number.isFinite(e[k]),`Invalid ${k}`);
 assert(e.w>0&&e.h>0&&e.x>=0&&e.y>=0&&e.x+e.w<=W+0.01&&e.y+e.h<=H+0.01,'Element outside slide');
}
function textStyle(e,base={}){
 const v={...base,...e};
 return {typeface:v.fontFamily??'Arial',fontSize:asPx(v.fontSize??14),color:v.color??'#333333',
   bold:v.bold??false,italic:v.italic??false,alignment:v.align??'left',verticalAlignment:v.verticalAlign??'top',
   wrap:'square',autoFit:'none',insets:0,...(v.lineSpacing?{lineSpacing:v.lineSpacing/100}:{})};
}
function runs(e){
 return e.runs.map(r=>({run:r.text,style:{
  ...(r.fontSize?{fontSize:`${r.fontSize}pt`}:{}),...(r.fontFamily?{typeface:r.fontFamily}:{}),
  ...(r.color?{color:r.color}:{}),...(r.bold!==undefined?{bold:r.bold}:{}),...(r.italic!==undefined?{italic:r.italic}:{})
 }}));
}
export function validateScene(scene){
 fields(scene,['slideSizePt','slides','title']);
 const [W,H]=scene.slideSizePt??[720,405];
 assert(Number.isFinite(W)&&Number.isFinite(H)&&W>0&&H>0,'Invalid slide size');
 assert(Array.isArray(scene.slides)&&scene.slides.length>0,'No slides');
 for(const slide of scene.slides){
  fields(slide,['id','elements','background','notes']);
  assert(Array.isArray(slide.elements),'No elements');
  for(const e of slide.elements){
   assert(['text','rect','line','table','image'].includes(e.type),`Unsupported type ${e.type}`);
   const allowed={text:[...boxKeys,...styleKeys,'text','runs','fill','lineColor','lineWidth'],rect:[...boxKeys,'fill','lineColor','lineWidth'],line:['id','type','x1','y1','x2','y2','color','width'],image:[...boxKeys,'path','alt'],table:[...boxKeys,...styleKeys,'values','colWidths','rowHeights','headerRows','fills','cellStyles','fill','lineColor','lineWidth','padding','merges']}[e.type];fields(e,allowed);
   if(e.type==='line'){
    for(const k of ['x1','y1','x2','y2'])assert(Number.isFinite(e[k]),`Invalid line ${k}`);
    for(const [x,y] of [[e.x1,e.y1],[e.x2,e.y2]])assert(x>=0&&y>=0&&x<=W&&y<=H,'Line outside slide');
   }else rect(e,W,H);
   if(e.type==='text'){
    assert(typeof e.text==='string'||Array.isArray(e.runs),'No text');
    if(e.runs){assert(e.runs.every(r=>typeof r.text==='string'),'Invalid runs');
     for(const r of e.runs){fields(r,['text','fontSize','fontFamily','color','bold','italic']);if(r.fontSize!==undefined)assert(Number.isFinite(r.fontSize)&&r.fontSize>0,'Invalid run size');}
     if(e.text!==undefined)assert(e.runs.map(r=>r.text).join('')===e.text,'Run/text mismatch');}
   }
   if(e.fontSize!==undefined)assert(Number.isFinite(e.fontSize)&&e.fontSize>0,'Invalid font size');
   if(e.type==='table'){
    assert(Array.isArray(e.values)&&e.values.length>0&&e.values[0].length>0,'Empty table');
    const R=e.values.length,C=e.values[0].length;
    assert(e.values.every(row=>Array.isArray(row)&&row.length===C),'Ragged table');
    assert(e.values.flat().every(v=>v===null||typeof v==='string'||(typeof v==='number'&&Number.isFinite(v))),'Invalid table value');
    if(e.headerRows!==undefined)assert(Number.isInteger(e.headerRows)&&e.headerRows>=0&&e.headerRows<=R,'Invalid headerRows');
    for(const [key,n,sum] of [['colWidths',C,e.w],['rowHeights',R,e.h]])if(e[key]){
     assert(e[key].length===n&&e[key].every(x=>Number.isFinite(x)&&x>0),`Invalid ${key}`);
     assert(Math.abs(e[key].reduce((a,b)=>a+b,0)-sum)<0.01,`${key} sum mismatch`);
    }
    assert(!e.merges,'This scene adapter does not implement table merges; use direct native authoring');
    if(e.cellStyles)assert(e.cellStyles.length===R&&e.cellStyles.every(r=>r.length===C),'Invalid cellStyles');
    if(e.fills)assert(e.fills.length===R&&e.fills.every(r=>r.length===C),'Invalid fills');
   }
  }
 }
 return [W,H];
}
export async function build(scene,{baseDir=process.cwd(),outputDir,registerFonts=true}={}){
 const [W,H]=validateScene(scene);await fs.mkdir(outputDir,{recursive:true});
 if(registerFonts){
  const full=path.join(here,'../assets/author-profile/fonts/FrankRuhlLibre-variable.ttf');
  try {FontLibrary.use('Frank Ruhl Libre',[full]);}catch(e){throw new Error(`Reference title font unavailable: ${e.message}`);}
 }
 const p=Presentation.create({slideSize:{width:asPx(W),height:asPx(H)}});
 for(const [si,ss] of scene.slides.entries()){
  const s=p.slides.add();s.background.fill=ss.background??'#FFFFFF';
  for(const [ei,e] of ss.elements.entries()){
   const name=e.id??`${ss.id??si}-${ei}`;
   if(['text','rect'].includes(e.type)){
    const shape=s.shapes.add({name,geometry:e.type==='text'?'textbox':'rect',position:pos(e),
     fill:e.fill??'none',line:{fill:e.lineColor??'none',width:asPx(e.lineWidth??0),style:'solid'}});
    if(e.type==='text'){
     shape.text.style=textStyle(e);shape.text=e.runs?[runs(e)]:(e.text??'');
    }
   }else if(e.type==='line'){
    const dx=e.x2-e.x1,dy=e.y2-e.y1;
    s.shapes.add({name,geometry:'line',position:{left:asPx(Math.min(e.x1,e.x2)),top:asPx(Math.min(e.y1,e.y2)),
     width:asPx(Math.max(Math.abs(dx),0.001)),height:asPx(Math.max(Math.abs(dy),0.001)),verticalFlip:dx*dy<0},
     fill:'none',line:{fill:e.color??'#555555',width:asPx(e.width??0.6),style:'solid'}});
   }else if(e.type==='image'){
    assert(e.path,'PPTX adapter requires image.path; remote URLs must be sourced through the host first');
    const bytes=await fs.readFile(path.resolve(baseDir,e.path));
    const contentType=bytes.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10]))?'image/png':
      (bytes[0]===255&&bytes[1]===216)?'image/jpeg':
      (bytes.subarray(0,4).toString()==='RIFF'&&bytes.subarray(8,12).toString()==='WEBP')?'image/webp':null;
    assert(contentType,'Unsupported image type');
    s.images.add({name,blob:bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),contentType,alt:e.alt??name,fit:'contain',position:pos(e)});
   }else if(e.type==='table'){
    const R=e.values.length,C=e.values[0].length;
    const t=s.tables.add({rows:R,columns:C,...{left:asPx(e.x),top:asPx(e.y),width:asPx(e.w),height:asPx(e.h)},
      values:e.values.map(row=>row.map(v=>v===null?'':String(v))),
      ...(e.colWidths?{columnWidths:e.colWidths.map(asPx)}:{})});
    t.styleOptions={headerRow:false,bandedRows:false,bandedColumns:false,firstColumn:false,lastColumn:false,totalRow:false};
    t.borders.assign({style:'solid',fill:e.lineColor??'#999999',width:asPx(e.lineWidth??0.5)});
    for(let r=0;r<R;r++){
     t.rows[r].height=asPx(e.rowHeights?.[r]??e.h/R);
     for(let c=0;c<C;c++){
      const st=e.cellStyles?.[r]?.[c]??{};
      const cell=t.getCell(r,c);
      const fv=Object.hasOwn(st,'fill')?st.fill:(e.fills?e.fills[r][c]:(Object.hasOwn(e,'fill')?e.fill:'#FFFFFF'));
      cell.fill=fillValue(fv);
      cell.text.style=textStyle(st,{fontFamily:e.fontFamily??'Arial',fontSize:e.fontSize??10,color:e.color??'#000000',bold:r<(e.headerRows??0),align:'center',verticalAlign:'middle'});
      t.cells.block({row:r,column:c,rowCount:1,columnCount:1}).assign({margins:{top:asPx(e.padding??1),bottom:asPx(e.padding??1),left:asPx(e.padding??1),right:asPx(e.padding??1)}});
     }
    }
   }
  }
  if(ss.notes)s.speakerNotes.text=ss.notes;
  await fs.writeFile(path.join(outputDir,`slide-${ss.id??si+1}.png`),new Uint8Array(await (await p.export({slide:s,format:'png',scale:1.5})).arrayBuffer()));
  const layout=await s.export({format:'layout'});await fs.writeFile(path.join(outputDir,`slide-${ss.id??si+1}.layout.json`),await layout.text());
 }
 await (await PresentationFile.exportPptx(p)).save(path.join(outputDir,'draft.pptx'));
 return p;
}
if(process.argv[1]&&import.meta.url===pathToFileURL(path.resolve(process.argv[1])).href){
 const [src,out]=process.argv.slice(2);assert(src&&out,'Usage: node compile_pptx.mjs scene.json output-dir');
 const scene=JSON.parse(await fs.readFile(src,'utf8'));
 await build(scene,{baseDir:path.dirname(path.resolve(src)),outputDir:path.resolve(out)});
}
