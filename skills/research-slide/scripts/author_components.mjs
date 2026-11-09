/** Native scientific components for this private author's research decks.
 * Public input geometry/font sizes are points; only this module converts to px.
 * Resolve @oai/artifact-tool from the host runtime. Never ship node_modules.
 */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
const hostRequire=createRequire(import.meta.resolve('@oai/artifact-tool'));
const {FontLibrary}=hostRequire('skia-canvas');
const here=path.dirname(fileURLToPath(import.meta.url));
const PX=4/3;
const px=n=>n*PX;
const assert=(condition,message)=>{if(!condition)throw new Error(`author-components: ${message}`);};
const finite=(v,key,{positive=false,nonnegative=false}={})=>{
 assert(typeof v==='number'&&Number.isFinite(v),`${key} must be finite`);
 assert(!positive||v>0,`${key} must be positive`);assert(!nonnegative||v>=0,`${key} must be nonnegative`);return v;
};
const primitive=(v,key)=>{
 assert(v===null||typeof v==='string'||(typeof v==='number'&&Number.isFinite(v)),`${key} must be string, finite number or null`);
 return v===null?'':String(v);
};
const color=(v,fallback)=>v===null||v===''||v==='none'?'none':v??fallback;
let fontLoaded=false;
export function registerAuthorFont(fontPath=path.join(here,'../assets/author-profile/fonts/FrankRuhlLibre-variable.ttf')){
 if(!fontLoaded){assert(fs.existsSync(fontPath),`full author title font missing: ${fontPath}`);FontLibrary.use('Frank Ruhl Libre',[fontPath]);fontLoaded=true;}
 return 'Frank Ruhl Libre';
}
registerAuthorFont();
let chromeFontLoaded=false;
export function registerAuthorChromeFont(fontPath=path.join(here,'../assets/author-profile/fonts/Montserrat-variable.ttf')){
 if(!chromeFontLoaded){assert(fs.existsSync(fontPath),`full author chrome font missing: ${fontPath}`);FontLibrary.use('Montserrat',[fontPath]);chromeFontLoaded=true;}
 return 'Montserrat';
}
registerAuthorChromeFont();

function textStyle(c={}){
 finite(c.fontSize??14,'fontSize',{positive:true});finite(c.lineSpacing??100,'lineSpacing',{positive:true});
 return {typeface:c.fontFamily??'Arial',fontSize:px(c.fontSize??14),color:c.color??'#333333',bold:c.bold??false,
  italic:c.italic??false,alignment:c.align??'left',verticalAlignment:c.verticalAlign??'top',
  insets:0,wrap:'square',autoFit:'none',lineSpacing:(c.lineSpacing??100)/100};
}
function box(c){
 for(const k of ['x','y'])finite(c[k],k,{nonnegative:true});for(const k of ['w','h'])finite(c[k],k,{positive:true});
 return {left:px(c.x),top:px(c.y),width:px(c.w),height:px(c.h)};
}
export function authorText(slide,c){
 const position=box(c);assert(typeof c.text==='string'||Array.isArray(c.runs),'text or runs required');
 if(c.runs&&c.text!==undefined)assert(c.runs.map(r=>r.text).join('')===c.text,'run/text mismatch');
 const shape=slide.shapes.add({name:c.name??'author-text',geometry:'textbox',position,fill:'none',line:{fill:'none',width:0}});
 shape.text.style=textStyle(c);
 shape.text=c.runs?[c.runs.map(r=>({run:r.text,style:{
  ...(r.fontSize!==undefined?{fontSize:`${r.fontSize}pt`}:{}),...(r.fontFamily?{typeface:r.fontFamily}:{}),
  ...(r.bold!==undefined?{bold:r.bold}:{}),...(r.italic!==undefined?{italic:r.italic}:{}),...(r.color?{color:r.color}:{})
 }}))]:(c.text??'');
 return shape;
}
export function addFooter(slide,{pageNumber,text='',x=28,y=365,w=660,h=12,fontSize=8,color:ink='#57068C'}={}){
 const objects=[];
 if(text)objects.push(authorText(slide,{x,y,w:w-40,h,text,fontSize,color:ink}));
 if(pageNumber!==undefined)objects.push(authorText(slide,{x:x+w-35,y,w:35,h,text:String(pageNumber),fontSize,color:ink,align:'right'}));
 return objects;
}
// One shared invariant record for native chrome and stage packets.
export const AUTHOR_CHROME_PROFILE=JSON.parse(fs.readFileSync(path.join(here,'../assets/author-profile/chrome.json'),'utf8'));
const CHROME_BY_SLIDE=new WeakMap();
function chromeGeometry(value,defaults,key){
 assert(value===undefined||typeof value==='boolean'||(value&&typeof value==='object'&&!Array.isArray(value)),`${key} must be boolean or pt geometry`);
 if(value===false)return null;
 const g={...defaults,...(typeof value==='object'?value:{})};box(g);
 assert(g.x+g.w<=720+.001&&g.y+g.h<=405+.001,`${key} outside 720x405pt canvas`);return g;
}
function originalImage(slide,filename,geometry,alt){
 const bytes=fs.readFileSync(path.join(here,'../assets/author-profile',filename));
 // The original SAI payload is JPEG even though its preserved filename ends .png.
 let contentType;
 if(bytes.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10])))contentType='image/png';
 else if(bytes[0]===255&&bytes[1]===216)contentType='image/jpeg';
 else throw new Error(`author-components: unsupported original image payload: ${filename}`);
 assert(bytes.length>32,`empty original image ${filename}`);
 return slide.images.add({blob:bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),contentType,alt,fit:'contain',position:box(geometry)});
}

/** Insert exact bundled branding on a blank 720x405pt page. Family is mandatory.
 * Existing native templates keep their own chrome: pass existingChrome:true or
 * do not call this helper. Repeated calls on a marked/live slide are skipped.
 */
export function addAuthorChrome(slide,c={}){
 assert(c.family==='sai'||c.family==='nyu',"family must explicitly be 'sai' or 'nyu'");
 const profile=AUTHOR_CHROME_PROFILE, family=profile.families[c.family];
 assert(c.variant===undefined||Object.hasOwn(profile.variants,c.variant),'unknown measured chrome variant');
 const variant=c.variant===undefined?null:profile.variants[c.variant];
 const strip=chromeGeometry(c.topStrip,family.topStrip.geometry,'topStrip');
 const logo=chromeGeometry(c.logo,family.logoGeometry,'logo');
 const marker=chromeGeometry(c.pageMarker,variant?.pageMarker?.geometry??profile.pageMarker.geometry,'pageMarker');
 const occupiedFooterRegions=[];
 if(logo)occupiedFooterRegions.push({kind:'logo',...logo});
 if(marker&&c.pageNumber!==undefined)occupiedFooterRegions.push({kind:'pageNumber',...marker});
 if(c.existingChrome===true)return {objects:[],images:[],pageMarker:null,skipped:true,reason:'caller-preserves-existing-template',occupiedFooterRegions};
 const previous=CHROME_BY_SLIDE.get(slide);
 if(previous)return {...previous,skipped:true,reason:'already-added-on-this-live-slide'};
 const marked=slide.images.items.some(image=>typeof image.alt==='string'&&image.alt.startsWith('Author chrome:'));
 if(marked)return {objects:[],images:[],pageMarker:null,skipped:true,reason:'existing-marked-native-chrome',occupiedFooterRegions};
 const images=[],objects=[];
 if(strip)images.push(originalImage(slide,family.topStrip.asset,strip,'Author chrome: original top strip'));
 if(logo)images.push(originalImage(slide,family.asset,logo,`Author chrome: original ${c.family} logo`));
 objects.push(...images);
 let pageMarker=null;
 if(marker&&c.pageNumber!==undefined){
  const value=primitive(c.pageNumber,'pageNumber');assert(value.length>0,'pageNumber must not be empty');
  pageMarker=authorText(slide,{...marker,text:value,fontFamily:c.pageFontFamily??profile.pageMarker.fontFamily,bold:c.pageBold??profile.pageMarker.bold,
   fontSize:c.pageFontSize??profile.pageMarker.fontSizePt,color:c.pageColor??profile.pageMarker.color,align:profile.pageMarker.align,name:'author-chrome-page-number'});
  objects.push(pageMarker);
 }
 const result={objects,images,pageMarker,skipped:false,family:c.family,occupiedFooterRegions,occupiedTopRegions:strip?[{kind:'topStrip',...strip}]:[]};
 CHROME_BY_SLIDE.set(slide,result);return result;
}

/** Editable paragraphs with native bullet metadata, never typed marker text.
 * Point geometry is converted once: marL/indent=EMU, spacing=1/100pt.
 * Levels remain real paragraph levels (0..2), with a hanging indent per level.
 */
export function addAuthorBullets(slide,c){
 const position=box(c);assert(Array.isArray(c.items)&&c.items.length>0,'bullet items required');
 const baseSize=c.fontSize??14,baseFamily=c.fontFamily??'Arial';
 const baseMargin=c.marginLeftPt??36,hanging=c.hangingPt??27,step=c.levelIndentPt??36;
 finite(baseSize,'fontSize',{positive:true});finite(baseMargin,'marginLeftPt',{nonnegative:true});finite(hanging,'hangingPt',{positive:true});finite(step,'levelIndentPt',{nonnegative:true});
 assert(baseMargin>=hanging,'marginLeftPt must be at least hangingPt');
 const markers=c.bulletCharacters??['●','○','■'];assert(Array.isArray(markers)&&markers.length===3&&markers.every(v=>typeof v==='string'&&[...v].length===1),'bulletCharacters must contain three single glyphs');
 const levels=[];
 const paragraphs=c.items.map((item,i)=>{
  assert(item&&typeof item==='object'&&!Array.isArray(item),`bullet item ${i} must be object`);
  const level=item.level??0;assert(Number.isInteger(level)&&level>=0&&level<=2,`bullet item ${i} level must be 0,1,2`);levels.push(level);
  assert(typeof item.text==='string'||Array.isArray(item.runs),`bullet item ${i} text/runs required`);
  const input=item.runs??[{text:item.text}];assert(input.length>0&&input.every(r=>r&&typeof r.text==='string'),`bullet item ${i} invalid runs`);
  const joined=input.map(r=>r.text).join('');assert(joined.trim().length>0,`bullet item ${i} is empty`);
  assert(!/[\r\n]/.test(joined),`bullet item ${i}: use a separate item for a new paragraph`);
  if(item.runs&&item.text!==undefined)assert(joined===item.text,`bullet item ${i} run/text mismatch`);
  const margin=item.marginLeftPt??(baseMargin+step*level),hang=item.hangingPt??hanging;
  const after=item.spaceAfter??c.spaceAfter??0,before=item.spaceBefore??0,lineSpacing=item.lineSpacing??c.lineSpacing??100;
  finite(margin,`item ${i} marginLeftPt`,{nonnegative:true});finite(hang,`item ${i} hangingPt`,{positive:true});assert(margin>=hang,`item ${i} hanging exceeds margin`);
  finite(after,`item ${i} spaceAfter`,{nonnegative:true});finite(before,`item ${i} spaceBefore`,{nonnegative:true});finite(lineSpacing,`item ${i} lineSpacing`,{positive:true});
  const runs=input.map((run,j)=>{
   const size=run.fontSize??item.fontSize??baseSize;finite(size,`bullet ${i} run ${j} fontSize`,{positive:true});
   return {run:run.text,style:{typeface:run.fontFamily??item.fontFamily??baseFamily,fontSize:`${size}pt`,
    color:run.color??item.color??c.color??'#333333',bold:run.bold??item.bold??false,italic:run.italic??item.italic??false}};
  });
  return {bulletCharacter:markers[level],marginLeft:Math.round(margin*12700),indent:-Math.round(hang*12700),
   spaceAfter:Math.round(after*100),spaceBefore:Math.round(before*100),paragraphStyle:{bulletCharacter:markers[level],
    bulletTypeface:item.bulletFontFamily??c.bulletFontFamily??item.fontFamily??baseFamily,
    lineSpacingPercent:Math.round(lineSpacing*1000),tabStops:[]},runs};
 });
 const shape=slide.shapes.add({name:c.name??'author-native-bullets',geometry:'textbox',position,fill:'none',line:{fill:'none',width:0}});
 shape.text.style=textStyle({...c,fontSize:baseSize,fontFamily:baseFamily});shape.text=paragraphs;
 assert(shape.text.paragraphs.items.length===paragraphs.length,'unexpected paragraph split');
 levels.forEach((level,i)=>{shape.text.paragraphs.getItem(i).level=level;});
 return shape;
}

function checkedSizes(sizes,n,total,key){
 const out=sizes??Array(n).fill(total/n);assert(Array.isArray(out)&&out.length===n,`${key} must have ${n} entries`);
 out.forEach((v,i)=>finite(v,`${key}[${i}]`,{positive:true}));
 assert(Math.abs(out.reduce((a,b)=>a+b,0)-total)<.001,`${key} must sum to frame dimension`);return [...out];
}
function cellStyleAt(styles,r,c,totalRows,columns){
 if(styles===undefined)return {};
 if(Array.isArray(styles)){
  assert(styles.length===totalRows&&styles.every(row=>Array.isArray(row)&&row.length===columns),'cellStyles matrix must match complete table, including headers');
  return styles[r][c]??{};
 }
 assert(styles&&typeof styles==='object','cellStyles must be full matrix or object keyed "row,column"');
 for(const key of Object.keys(styles)){
  assert(/^\d+,\d+$/.test(key),`invalid cellStyles key ${key}`);const [rr,cc]=key.split(',').map(Number);
  assert(rr<totalRows&&cc<columns,`cellStyles key outside table: ${key}`);
 }
 return styles[`${r},${c}`]??{};
}
function applyCell(table,r,c,style,{fill='#FFFFFF',padding=1}={}){
 const cell=table.getCell(r,c);cell.fill=color(style.fill,fill);
 cell.text.style=textStyle(style);
 table.cells.block({row:r,column:c,rowCount:1,columnCount:1}).assign({margins:{top:px(padding),bottom:px(padding),left:px(padding),right:px(padding)}});
}

/** A native table with two header rows and optional body-relative merges.
 * groups: [{label,start,end}] inclusive column indices. Uncovered columns merge
 * both header rows vertically. merges: [{startRow,endRow,startColumn,endColumn}]
 * indexes BODY rows, not headers. Distinct covered values are refused.
 * cellStyles indexes the full table including both headers (r=0,1).
 */
export function addGroupedTable(slide,c){
 const position=box(c);assert(Array.isArray(c.columns)&&c.columns.length>0,'columns required');
 const labels=c.columns.map((v,i)=>primitive(v,`columns[${i}]`));const C=labels.length;
 assert(Array.isArray(c.rows)&&c.rows.length>0,'body rows required');
 const rows=c.rows.map((row,r)=>{assert(Array.isArray(row)&&row.length===C,`body row ${r} column count mismatch`);return row.map((v,k)=>primitive(v,`rows[${r}][${k}]`));});
 const R=rows.length+2,cw=checkedSizes(c.colWidths,C,c.w,'colWidths'),rh=checkedSizes(c.rowHeights,R,c.h,'rowHeights');
 const values=[Array(C).fill(''),[...labels],...rows.map(r=>[...r])],merges=[],covered=new Set();
 for(const [i,g] of (c.groups??[]).entries()){
  const {start,end}=g;assert(Number.isInteger(start)&&Number.isInteger(end)&&start>=0&&end>=start&&end<C,`invalid group ${i}`);
  for(let col=start;col<=end;col++){assert(!covered.has(col),`overlapping group at column ${col}`);covered.add(col);}
  values[0][start]=primitive(g.label,`groups[${i}].label`);
  if(end>start)merges.push({startRow:0,endRow:0,startColumn:start,endColumn:end});
 }
 for(let col=0;col<C;col++)if(!covered.has(col)){
  values[0][col]=labels[col];values[1][col]='';merges.push({startRow:0,endRow:1,startColumn:col,endColumn:col});
 }
 const occupied=new Set();
 for(const [i,m] of (c.merges??[]).entries()){
  for(const k of ['startRow','endRow','startColumn','endColumn'])assert(Number.isInteger(m[k]),`merge ${i}.${k} must be integer`);
  assert(m.startRow>=0&&m.endRow>=m.startRow&&m.endRow<rows.length&&m.startColumn>=0&&m.endColumn>=m.startColumn&&m.endColumn<C,`merge ${i} outside body`);
  const anchor=values[m.startRow+2][m.startColumn];
  for(let r=m.startRow;r<=m.endRow;r++)for(let col=m.startColumn;col<=m.endColumn;col++){
   const key=`${r},${col}`;assert(!occupied.has(key),`overlapping body merge ${key}`);occupied.add(key);
   assert(values[r+2][col]===''||values[r+2][col]===anchor,`merge ${i} would discard distinct value at body ${r},${col}`);
   if(r!==m.startRow||col!==m.startColumn)values[r+2][col]='';
  }
  if(m.startRow!==m.endRow||m.startColumn!==m.endColumn)merges.push({...m,startRow:m.startRow+2,endRow:m.endRow+2});
 }
 const table=slide.tables.add({rows:R,columns:C,...position,values,columnWidths:cw.map(px)});
 table.styleOptions={headerRow:false,bandedRows:false,bandedColumns:false,firstColumn:false,lastColumn:false,totalRow:false};
 table.borders.assign({style:'solid',fill:color(c.gridColor,'#333333'),width:px(c.gridWidth??.5)});
 for(let r=0;r<R;r++){
  table.rows[r].height=px(rh[r]);
  for(let col=0;col<C;col++){
   const override=cellStyleAt(c.cellStyles,r,col,R,C);assert(override&&typeof override==='object'&&!Array.isArray(override),`invalid style ${r},${col}`);
   const style={fontSize:c.fontSize??9.5,fontFamily:c.fontFamily??'Arial',color:c.textColor??'#000000',align:c.align??'center',
    verticalAlign:'middle',bold:r<2?(c.headerBold??true):false,...override};
   applyCell(table,r,col,style,{fill:r<2?color(c.headerFill,'#CCCCCC'):color(c.bodyFill,'#FFFFFF'),padding:c.padding??1});
  }
 }
 for(const range of merges)table.merge(range);
 return {table,headerRows:2,bodyRowOffset:2,values,mergeRanges:merges,colWidths:cw,rowHeights:rh};
}

/** A vertical, channel-aligned pipeline made from native one-row tables.
 * Stage values must all have the same count; strings are preserved exactly.
 * Labels sit to the left; optional formula is editable plain text below a row.
 * Connector arrows are native, unbound endpoints (do not claim they follow tables).
 */
export function addVectorPipeline(slide,c){
 finite(c.x,'x',{nonnegative:true});finite(c.y,'y',{nonnegative:true});finite(c.w,'w',{positive:true});
 assert(Array.isArray(c.stages)&&c.stages.length>0,'pipeline stages required');
 const N=c.stages[0].values?.length;assert(Number.isInteger(N)&&N>0,'stage values required');
 for(const [i,stage] of c.stages.entries())assert(stage.connectToNext===undefined||typeof stage.connectToNext==='boolean',`stage ${i} connectToNext must be boolean`);
 const rowHeight=c.rowHeight??20,gap=c.gap??18,labelWidth=c.labelWidth??130,fontSize=c.fontSize??11;
 [rowHeight,gap,labelWidth,fontSize].forEach((n,i)=>finite(n,['rowHeight','gap','labelWidth','fontSize'][i],{positive:true}));
 assert(c.w>labelWidth+N*8,'pipeline width too small for label and channels');
 const vectorX=c.x+labelWidth,vectorW=c.w-labelWidth,cw=checkedSizes(c.colWidths,N,vectorW,'colWidths');
 const tables=[],labels=[],formulas=[],arrows=[];
 for(const [i,stage] of c.stages.entries()){
  assert(Array.isArray(stage.values)&&stage.values.length===N,`stage ${i} must preserve all ${N} channels`);
  assert(stage.values.every(v=>typeof v==='string'),`stage ${i} values must be strings to preserve precision`);
  assert(typeof stage.label==='string',`stage ${i} label required`);
  if(stage.cellStyles!==undefined)assert(Array.isArray(stage.cellStyles)&&stage.cellStyles.length===N,`stage ${i} cellStyles must match ${N} channels`);
  const y=c.y+i*(rowHeight+gap);
  labels.push(authorText(slide,{x:c.x,y,w:labelWidth-16,h:rowHeight,text:stage.label,fontSize:c.labelFontSize??fontSize,
   fontFamily:c.fontFamily??'Arial',color:c.textColor??'#000000',verticalAlign:'middle',bold:stage.bold??false}));
  const table=slide.tables.add({rows:1,columns:N,left:px(vectorX),top:px(y),width:px(vectorW),height:px(rowHeight),values:[[...stage.values]],columnWidths:cw.map(px)});
  table.styleOptions={headerRow:false,bandedRows:false,bandedColumns:false,firstColumn:false,lastColumn:false,totalRow:false};
  table.rows[0].height=px(rowHeight);
  table.borders.assign({style:'solid',fill:color(c.gridColor,'#333333'),width:px(c.gridWidth??.5)});
  for(let col=0;col<N;col++){
   const st=stage.cellStyles?.[col]??{};
   applyCell(table,0,col,{fontSize,fontFamily:c.fontFamily??'Arial',color:c.textColor??'#000000',align:'center',verticalAlign:'middle',...st},
    {fill:color(stage.fill,c.fill??'#FFFFFF'),padding:c.padding??1});
  }
  tables.push(table);
  if(stage.formula!==undefined){
   assert(typeof stage.formula==='string',`stage ${i}.formula must be text`);
   const fh=c.formulaHeight??Math.min(gap-3,(c.formulaFontSize??9.5)*1.5);
   assert(fh>0,'gap too small for formula');
   formulas.push(authorText(slide,{x:vectorX,y:y+rowHeight+2,w:vectorW,h:fh,text:stage.formula,fontSize:c.formulaFontSize??9.5,
    fontFamily:c.formulaFontFamily??'Arial',color:c.textColor??'#000000'}));
  }
  if(i<c.stages.length-1&&stage.connectToNext!==false){
   arrows.push(slide.shapes.add({name:`pipeline-step-${i+1}`,geometry:'connector',kind:'straight',
    position:{left:px(vectorX-8),top:px(y+rowHeight+1),width:0,height:px(gap-2)},
    line:{fill:c.arrowColor??'#333333',width:px(c.arrowWidth??.7)},tail:{type:'triangle',width:'sm',length:'sm'}}));
  }
 }
 return {tables,labels,formulas,arrows,channelCount:N,vectorX,vectorWidth:vectorW,
  boundsPt:{x:c.x,y:c.y,w:c.w,h:c.stages.length*rowHeight+(c.stages.length-1)*gap+(c.stages.at(-1).formula!==undefined?gap:0)}};
}
