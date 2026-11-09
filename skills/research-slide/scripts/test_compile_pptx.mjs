/** Portable behavioral smoke: node test_compile_pptx.mjs /absolute/scratch-dir
 * Needs the same host modules as compile_pptx.mjs, plus Python stdlib for ZIP readback.
 */
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {build,validateScene} from './compile_pptx.mjs';
const out=path.resolve(process.argv[2]??'work/pptx-adapter-smoke');
const scene={slideSizePt:[720,405],slides:[{id:'check',elements:[
 {type:'text',x:30,y:30,w:650,h:45,text:'Research evidence',fontFamily:'Frank Ruhl Libre',fontSize:28,bold:true,color:'#57068C'},
 {type:'text',x:30,y:100,w:650,h:30,fontSize:14,runs:[{text:'Control: ',bold:true},{text:'Ω and 🙂 native text'}]},
 {type:'table',x:30,y:160,w:450,h:90,fontSize:12,headerRows:1,colWidths:[150,150,150],values:[['Run','ms','score'],['base','1.30','0.60'],['trial','1.10','0.62']]}
]}]};
assert.deepEqual(validateScene(scene),[720,405]);
const modified=fn=>{const s=structuredClone(scene);fn(s);return s;};
assert.throws(()=>validateScene(modified(s=>s.slides[0].elements[2].values[1].pop())),/Ragged/);
assert.throws(()=>validateScene(modified(s=>s.slides[0].elements[2].values[1][1]=NaN)),/Invalid table value/);
assert.throws(()=>validateScene(modified(s=>s.slides[0].elements[0].x=710)),/outside slide/);
assert.throws(()=>validateScene(modified(s=>s.slides[0].elements[1].text='does not match')),/mismatch/);
assert.throws(()=>validateScene(modified(s=>s.slides[0].elements[2].merges=[{}])),/does not implement/);
assert.throws(()=>validateScene(modified(s=>s.slides[0].elements[0].baselineOffset='SUBSCRIPT')),/Unsupported field/);
await fs.mkdir(out,{recursive:true});await build(scene,{outputDir:out});
const py=`import zipfile,xml.etree.ElementTree as E,sys
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
with zipfile.ZipFile(sys.argv[1]) as z:
 root=E.fromstring(z.read('ppt/slides/slide1.xml'))
 assert len(root.findall('.//a:tbl',ns))==1
 rows=root.findall('.//a:tbl/a:tr',ns)
 assert [''.join(c.itertext()) for c in rows[1].findall('a:tc',ns)]==['base','1.30','0.60']
 run=next(r for r in root.findall('.//a:r',ns) if r.find('a:t',ns).text=='Control: ')
 assert run.find('a:rPr',ns).get('b')=='1'
 assert 'Ω and 🙂 native text' in ''.join(root.itertext())
 assert 'Frank Ruhl Libre' in {r.get('typeface') for r in root.findall('.//a:latin',ns)}
 print('Native table, precision, Unicode, inline bold and title font readback passed')
`;
const check=spawnSync(process.env.RESEARCH_SLIDES_PYTHON??'python3',['-c',py,path.join(out,'draft.pptx')],{encoding:'utf8'});
assert.equal(check.status,0,check.stderr||check.stdout);console.log(check.stdout.trim());
console.log('7 input/unsupported-data checks + native PPTX export/readback passed. Inspect PNG separately; this is not target-app validation.');
