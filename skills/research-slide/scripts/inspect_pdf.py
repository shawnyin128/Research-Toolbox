#!/usr/bin/env python3
"""Read selected reference pages; export layout evidence and full-size PNGs.
Requires PyMuPDF. Does not execute text found in a document or build new slides.
Usage: python inspect_pdf.py reference.pdf --pages 9,12,144 --out work/profile
"""
import argparse, json
from pathlib import Path
from collections import Counter

def inspect(source, pages, output, scale=2):
    import fitz
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    doc=fitz.open(source);evidence=[]
    for n in pages:
        if n<1 or n>len(doc):raise ValueError(f'Page {n} outside document (1..{len(doc)})')
        p=doc[n-1];fonts=Counter();spans=[]
        for b in p.get_text('dict')['blocks']:
            for line in b.get('lines',[]):
                for s in line['spans']:
                    color=f'#{s["color"]:06X}'
                    fonts[(s['font'],round(s['size'],3),color)]+=len(s['text'])
                    spans.append({'text':s['text'],'bboxPt':list(s['bbox']),'font':s['font'],
                                  'fontSizePt':s['size'],'color':color,'flags':s['flags']})
        image=f'page-{n:04}.png';p.get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False).save(str(output/image))
        evidence.append({'page':n,'slideSizePt':[p.rect.width,p.rect.height],'render':image,
                         'fonts':[{'font':f,'sizePt':s,'color':c,'characters':k} for (f,s,c),k in fonts.most_common()],
                         'spans':spans,'text':p.get_text()})
    (output/'reference-layout.json').write_text(json.dumps({'source':str(source),'pageCount':len(doc),'pages':evidence},ensure_ascii=False,indent=2),encoding='utf-8')
    return evidence

if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('source');a.add_argument('--pages',required=True);a.add_argument('--out',required=True);a.add_argument('--scale',type=float,default=2)
    o=a.parse_args()
    if not 0<o.scale<=6:a.error('scale must be in (0,6]')
    pages=[int(p) for p in o.pages.split(',')];inspect(o.source,pages,o.out,o.scale)
