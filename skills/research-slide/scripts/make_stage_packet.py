#!/usr/bin/env python3
"""Build a narrow local context packet; never invokes a model or network."""
import argparse
import hashlib
import json
import re
from pathlib import Path
import shutil
from validate_contracts import ContractError, validate_facts, validate_layout, validate_copy

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / 'references'


def read_json(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def write_json(p, value):
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def example_number(filename):
    """Read an inventory identifier; never synthesize an image filename."""
    match = re.match(r'^example-(\d+)(?:[-.])', Path(filename).name)
    if not match:
        raise ContractError(f'example inventory lacks a numeric identifier: {filename}')
    return int(match.group(1))


def inventory():
    return read_json(REF / 'author-examples/family-inventory.json')['families']


def selected_reference(example=None, family_name=None):
    """Resolve one image and measurement through recorded inventory/provenance."""
    matches = [x for x in inventory() if
               (x['family'] == family_name if family_name else example_number(x['image']) == example)]
    if len(matches) != 1:
        raise ContractError('selected reference must resolve to one recorded inventory item')
    entry = matches[0]
    filename, fragment = entry['measurement'].split('#', 1)
    field, value = fragment.split('=', 1)
    measured = read_json(REF / 'author-examples' / filename)
    records = measured['records'] if isinstance(measured, dict) else measured
    records = [r for r in records if str(r.get(field)) == value and r['example'] == entry['image']]
    if len(records) != 1:
        raise ContractError('image/provenance inventory disagrees with measurement record')
    family = None
    focused = False
    if entry.get('layoutRecord'):
        layout_file, selector = entry['layoutRecord'].split('#', 1)
        key, selected = selector.split('=', 1)
        families = read_json(REF / 'author-examples' / layout_file)['families']
        matches = [f for f in families if f.get(key) == selected]
        if len(matches) != 1 or Path(matches[0]['trainingExample']).name != entry['image']:
            raise ContractError('selected layout provenance disagrees with image inventory')
        family = matches[0]
        focused = layout_file == 'focused-layout-starters.json'
    return {'number': example_number(entry['image']), 'family': family,
            'record': records[0], 'image': REF / 'author-examples' / entry['image'],
            'focused': focused, 'inventory': entry}


def geometry_style(selection):
    if selection['family']:
        # Language templates belong to COPY; geometry carries scientific role only.
        return {k: v for k, v in selection['family'].items() if k not in {'titleGrammar'}}
    item = selection['record']
    return {'example': item['example'], 'slideSizePt': item['slideSizePt'],
            'fonts': item['fontsByCharacterCount'],
            'titleMeasurements': [{k: v for k, v in t.items() if k != 'text'} for t in item['titles']],
            'spanGeometry': [dict({k: v for k, v in span.items() if k != 'text'},
                                  characterCount=len(span['text']),
                                  bullet=span['text'] if span['text'] in ['●', '○', '■'] else None)
                             for span in item['textSpans']],
            'note': 'Glyph bounds, not recovered text-box frames. Actual selected image supplies visual hierarchy.'}


def frozen_facts(data):
    """Field whitelist at every record boundary; never carry raw drafts by accident."""
    result = {k: data[k] for k in ('schemaVersion', 'caseId', 'audience', 'series', 'priorContext',
              'workingNames', 'selection') if k in data}
    fields = {
        'facts': {'id', 'role', 'delivery', 'statement', 'source', 'evidenceRef', 'locator',
                  'symbol', 'meaning', 'essential', 'priorDefinition'},
        'tables': {'id', 'source', 'columns', 'rows', 'columnMetadata'},
        'assets': {'id', 'source', 'path', 'sha256', 'integrityRequirements'},
        'equations': {'id', 'source', 'expression', 'definitions'}}
    for kind, allowed in fields.items():
        result[kind] = [{k: v for k, v in item.items() if k in allowed} for item in data.get(kind, [])]
    if isinstance(result.get('selection'), dict):
        result['selection'] = {k: v for k,v in result['selection'].items() if k in {'footer', 'chromeVariant'}}
    for fact in result['facts']:
        if isinstance(fact.get('priorDefinition'), dict):
            fact['priorDefinition'] = {k:v for k,v in fact['priorDefinition'].items() if k in {'source','location'}}
    for equation in result['equations']:
        equation['definitions'] = [{k:v for k,v in d.items() if k in {'symbol','meaning'}} for d in equation.get('definitions',[])]
    for table in result['tables']:
        if 'columnMetadata' in table:
            table['columnMetadata'] = [{k: v for k, v in col.items() if k in
                {'columnIndex', 'meaning', 'unit', 'direction', 'aggregation', 'scope'}}
                for col in table['columnMetadata']]
    return result


def approved_plan(value):
    """Exclude upstream raw archives/drafts even if attached to approved geometry."""
    excluded = {'rawNotes', 'rawParagraphs', 'privateSourceDraft', 'draftedBodySentences',
                'sourceVerbatim', 'approvedCopyDraft', 'copyDraft', 'reviews', 'oldReviews'}
    if isinstance(value, dict):
        return {k: approved_plan(v) for k, v in value.items() if k not in excluded}
    if isinstance(value, list):
        return [approved_plan(v) for v in value]
    return value


def style_check_packet(a, ap):
    if not (a.example or a.family) or (a.example and a.family):
        ap.error('style-check requires exactly one selected --example or --family')
    if not a.saved_page or not a.intent:
        ap.error('style-check requires --saved-page PNG and --intent JSON')
    if any((a.facts, a.layout, a.copy, a.selection, a.candidates, a.evidence)):
        ap.error('style-check excludes facts, layout/copy drafts, selection reviews and scientific evidence dumps')
    try:
        selection = selected_reference(a.example, a.family)
        intent = read_json(a.intent)
        if not all(isinstance(intent.get(k), str) and intent[k].strip() for k in ('argumentRole', 'audience')):
            raise ContractError('intent needs argumentRole and audience')
        saved = Path(a.saved_page)
        if not saved.is_file() or saved.read_bytes()[:8] != b'\x89PNG\r\n\x1a\n':
            raise ContractError('saved-page must be an actual PNG render of the saved file')
        dst = Path(a.out).resolve()
        if dst.exists() and any(dst.iterdir()):
            raise ContractError('output packet must be empty')
        dst.mkdir(parents=True, exist_ok=True)
        shutil.copy2(saved, dst / 'saved-page.png')
        shutil.copy2(selection['image'], dst / 'style-reference.png')
        shutil.copy2(REF / 'saved-page-style-check.md', dst / 'stage-guide.md')
        write_json(dst / 'style-measurements.json', geometry_style(selection))
        write_json(dst / 'intent.json', {k: intent[k] for k in ('argumentRole', 'audience')})
        files = ['saved-page.png', 'style-reference.png', 'stage-guide.md', 'style-measurements.json', 'intent.json']
        write_json(dst / 'packet-manifest.json', {'stage': 'style-check', 'files': files,
            'example': selection['number'], 'family': selection['inventory']['family'],
            'fileSha256': {n: hashlib.sha256((dst / n).read_bytes()).hexdigest() for n in files},
            'scope': 'Fresh saved-page style critic only; no prior reviews or copy drafts. Separate fresh science review follows repairs.'})
    except (ContractError, OSError, ValueError) as e:
        ap.error(str(e))
    print(json.dumps({'packet': str(dst), 'stage': 'style-check', 'files': files}))


def localize_links(path, targets):
    """Keep only links to files actually carried in the isolated packet."""
    text = path.read_text(encoding='utf-8')
    def replace(match):
        label, target = match.group(1), match.group(2)
        return f'[{label}]({targets[target]})' if target in targets else label
    path.write_text(re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replace, text), encoding='utf-8')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('stage', choices=['select', 'layout', 'copy', 'assembly', 'style-check'])
    ap.add_argument('--facts')
    ap.add_argument('--saved-page')
    ap.add_argument('--intent')
    ap.add_argument('--layout')
    ap.add_argument('--copy')
    ap.add_argument('--example', type=int)
    ap.add_argument('--family')
    ap.add_argument('--candidates', type=int, nargs=2,
                    help='Two functionally plausible examples for an isolated selection decision')
    ap.add_argument('--selection', help='Frozen same-case selection decision, carried into layout')
    ap.add_argument('--specialist', choices=['mechanism', 'experiment', 'ablation', 'workflow'])
    ap.add_argument('--backend', choices=['pptx', 'google'], default='pptx')
    ap.add_argument('--out', required=True)
    ap.add_argument('--evidence', action='append', default=[], help='Explicit permitted scientific asset to copy into the packet; repeat as needed')
    a = ap.parse_args()
    if a.stage == 'style-check':
        style_check_packet(a, ap)
        return
    if not a.facts or not a.specialist:
        ap.error('--facts and --specialist required for authoring stages')
    if a.saved_page or a.intent:
        ap.error('--saved-page/--intent are only for style-check')
    facts = read_json(a.facts)
    try:
        validate_facts(facts)
        if a.layout:
            validate_layout(facts, read_json(a.layout))
        if a.copy:
            validate_copy(facts, read_json(a.copy), read_json(a.layout) if a.layout else None)
    except ContractError as e:
        ap.error(str(e))
    if a.stage in ['select', 'layout'] and (a.layout or a.copy):
        ap.error('selection/layout packets cannot receive downstream layout/copy artifacts')
    if a.stage == 'select':
        if not a.candidates or len(set(a.candidates)) != 2 or a.example or a.family or a.selection:
            ap.error('select requires two distinct --candidates and no final selection/example/family')
    elif a.candidates:
        ap.error('--candidates is only for selection packets')
    if a.stage == 'copy' and a.copy:
        ap.error('copy packets cannot receive prior draft copy')
    if a.example and a.family:
        ap.error('select exactly one --example or --family')
    if a.stage in ['copy', 'assembly'] and not a.layout:
        ap.error('--layout is required for copy/assembly')
    if a.stage == 'assembly' and not a.copy:
        ap.error('--copy is required for assembly')
    if a.layout:
        layout = read_json(a.layout)
        if layout.get('stage') != 'layout' or layout.get('caseId') != facts['caseId']:
            ap.error('--layout must be a same-case layout-stage contract')
    if a.stage not in ['assembly', 'select'] and not (a.example or a.family):
        ap.error('select --example or --family before building the packet')
    selection = None
    family = None
    example = a.example
    if a.stage not in ['assembly', 'select'] or a.example or a.family:
        try:
            selection = selected_reference(a.example, a.family)
        except ContractError as e:
            ap.error(str(e))
        family = selection['family']
        example = selection['number']
        a.family = family['family'] if family else None
    selection_decision = read_json(a.selection) if a.selection else None
    if selection_decision:
        proposed = selection_decision.get('candidateExamples', [])
        if (not isinstance(proposed, list) or len(proposed) != 2 or
                not all(type(i) is int and i in {example_number(x['image']) for x in inventory()} for i in proposed) or
                len(set(proposed)) != 2 or
                not all(isinstance(selection_decision.get(k), str) and selection_decision[k].strip()
                        for k in ('reportIntent', 'objectRole', 'reason', 'alternativeRejection'))):
            ap.error('--selection requires two candidates and explicit argument-role rationale')
        if (a.stage != 'layout' or selection_decision.get('caseId') != facts['caseId'] or
                selection_decision.get('selectedExample') != example or
                example not in selection_decision.get('candidateExamples', [])):
            ap.error('--selection must be the same-case decision for the selected layout example')
    dst = Path(a.out).resolve()
    if dst.exists() and any(dst.iterdir()):
        ap.error('output packet must be empty; do not overwrite frozen stage inputs')
    dst.mkdir(parents=True, exist_ok=True)
    files = []
    facts = frozen_facts(facts)
    evidence_map = {}
    requested = {Path(p).resolve() for p in a.evidence}
    facts_dir = Path(a.facts).resolve().parent
    asset_sources = {item['id']: (Path(item['path']) if Path(item['path']).is_absolute()
                     else facts_dir / item['path']).resolve() for item in facts['assets']}
    expected = set(asset_sources.values())
    if requested != expected:
        ap.error('--evidence must contain exactly the assets declared in frozen facts')
    for source in a.evidence:
        p = Path(source).resolve()
        if not p.is_file():
            ap.error('scientific evidence must be an existing regular file')
        declared = [item for item in facts['assets'] if asset_sources[item['id']] == p]
        if any(hashlib.sha256(p.read_bytes()).hexdigest() != item['sha256'] for item in declared):
            ap.error('scientific evidence sha256 differs from frozen facts')
        target = dst / 'evidence' / p.name
        if target.exists():
            ap.error('evidence basenames must be distinct')
        target.parent.mkdir(exist_ok=True)
        shutil.copy2(p, target)
        files.append(target.relative_to(dst).as_posix())
        evidence_map[str(p)] = target.relative_to(dst).as_posix()
        for item in declared:
            item['path'] = target.relative_to(dst).as_posix()

    def doc(source, name):
        shutil.copy2(REF / source, dst / name)
        files.append(name)

    stage_name = {'select': '05-select', 'layout': '10-layout', 'copy': '20-copy', 'assembly': '30-assembly'}[a.stage]
    doc('stages/' + stage_name + '.md', 'stage-guide.md')
    if a.stage in {'layout', 'copy'}:
        doc('recovery-contract.md', 'recovery-contract.md')
    if a.stage == 'select':
        doc('layout/family-selector.md', 'family-selector.md')
        candidates = []
        for number in a.candidates:
            candidate = selected_reference(example=number)
            image_name = f'candidate-{number:02d}.png'
            shutil.copy2(candidate['image'], dst / image_name)
            files.append(image_name)
            if candidate['family']:
                summary = geometry_style(candidate)
            else:
                record = candidate['record']
                summary = {'titleLevelsPt': sorted({s['sizePt'] for s in record['textSpans'] if 'Frank' in s['font']}),
                           'typeLevelsPt': sorted({s['sizePt'] for s in record['textSpans']}),
                           'note': 'Inspect image for argument hierarchy; training science is not current content.'}
            candidates.append({'example': number, 'image': image_name, 'layoutEvidence': summary})
        write_json(dst / 'candidate-layouts.json', {'candidates': candidates,
            'scope': 'Layout evidence only. Choose by argument role before evidence form; reject both if neither fits.'})
        files.append('candidate-layouts.json')
        for name in ('stage-guide.md', 'family-selector.md'):
            localize_links(dst / name, {'../layout/family-selector.md': 'family-selector.md',
                                      '../author-examples/focused-layout-starters.json': 'candidate-layouts.json'})
    elif a.stage == 'layout':
        doc('layout/' + a.specialist + '.md', 'specialist.md')
        shutil.copy2(selection['image'], dst / 'style-reference.png')
        files.append('style-reference.png')
        doc('layout/family-selector.md', 'family-selector.md')
        selected_guide = Path(selection['inventory']['guide']).stem
        focused_module = selected_guide if selected_guide != a.specialist else None
        if focused_module:
            doc('layout/' + focused_module + '.md', 'focused-specialist.md')
        table_component = ('table' in selection['inventory'].get('evidenceForm', '').lower()
                           and selected_guide != 'scientific-table')
        if table_component:
            doc('layout/scientific-table.md', 'table-component.md')
        if family and family.get('detailImage'):
            detail = REF / 'author-examples' / Path(family['detailImage']).name
            shutil.copy2(detail, dst / 'style-detail.png')
            files.append('style-detail.png')
        style = geometry_style(selection)
        write_json(dst / 'layout-style.json', style)
        files.append('layout-style.json')
        # Selected science family supplies geometry; series selection supplies original chrome.
        chrome_file = ROOT / 'assets/author-profile/chrome.json'
        if not chrome_file.is_file():
            ap.error('canonical author-profile/chrome.json is required for isolated layout')
        chrome = read_json(chrome_file)
        brand = facts.get('selection', {}).get('footer')
        if brand not in chrome['families']:
            ap.error('facts.selection.footer must select a canonical chrome family')
        chosen = json.loads(json.dumps(chrome['families'][brand]))
        def copy_chrome_assets(node):
            if isinstance(node, dict):
                for key, value in node.items():
                    if key == 'asset' and isinstance(value, str):
                        src = chrome_file.parent / value
                        if node.get('assetSha256') and hashlib.sha256(src.read_bytes()).hexdigest() != node['assetSha256']:
                            ap.error('canonical brand asset sha256 mismatch')
                        target = dst / 'brand-assets' / src.name
                        target.parent.mkdir(exist_ok=True)
                        shutil.copy2(src, target)
                        node[key] = target.relative_to(dst).as_posix()
                        if node[key] not in files:
                            files.append(node[key])
                    else:
                        copy_chrome_assets(value)
            elif isinstance(node, list):
                for value in node:
                    copy_chrome_assets(value)
        copy_chrome_assets(chosen)
        # Copy fonts by the canonical manifest's explicit paths, when supplied.
        font_data = json.loads(json.dumps(chrome.get('fonts', {})))
        copy_chrome_assets(font_data)
        page_marker = chrome['pageMarker']
        variant = facts.get('selection', {}).get('chromeVariant')
        if variant:
            if variant not in chrome.get('variants', {}):
                ap.error('unknown explicit selection.chromeVariant')
            page_marker = {**page_marker, **chrome['variants'][variant].get('pageMarker', {})}
            for region in chosen.get('occupiedRegions', {}).get('footer', []):
                if region.get('kind') == 'pageNumber':
                    region.update(page_marker['geometry'])
        brand_style = {'version': chrome['version'], 'canvasPt': chrome['canvasPt'],
                       'selectedBrand': brand, 'family': chosen,
                       'selectedVariant': variant, 'pageMarker': page_marker, 'fonts': font_data}
        write_json(dst / 'brand-invariants.json', brand_style)
        files.append('brand-invariants.json')
    elif a.stage == 'copy':
        doc('copy/working-language.md', 'working-language.md')
        choice = {'mechanism': 'mechanism-text', 'experiment': 'experimental-claims',
                  'ablation': 'experimental-claims', 'workflow': 'workflow-status'}[a.specialist]
        doc('copy/' + choice + '.md', 'specialist.md')
        doc('copy/title.md', 'title.md')
        procedure_guide = a.family in {'algorithm-report-with-supporting-inset', 'paper-method-outline',
                                      'numbered-procedure-report', 'operator-graph'}
        if procedure_guide:
            doc('copy/method-procedure.md', 'procedure-guide.md')
        item = selection['record']
        spans = item['textSpans']
        # Title language is separate evidence, including an explicit absent-title case.
        titles = [s['text'] for s in spans if 'Frank' in s['font']]
        body = [s['text'] for s in spans if s.get('sizePt', s.get('fontSizePt', 0)) >= 12
                and 'Arial' in s['font'] and len(s['text']) > 8]
        style = {'example': item['example'], 'titleEvidence': {'present': bool(titles),
                 'actualText': titles, 'use': 'Title cadence only; retain the current method and component/purpose.'},
                 'bodyEvidence': {'voiceFragments': body},
                 'scope': 'Selected example only. Language evidence; current facts supply all scientific names, values and claims.'}
        if family and not selection['focused']:
            styles = read_json(REF / 'author-examples/author-family-copy.json')['families']
            selected = next(x for x in styles if x['family'] == a.family)
            allowed = ['roleHeading', 'roleHeadingStyle', 'roleHeadingWeight', 'structure']
            style.update({'family': a.family, 'workingCadence': selected['workingCadence'],
                          'proseTokens': {k: v for k, v in selected['proseTokens'].items() if k in allowed}})
        if family and selection['focused']:
            style.update({'family': a.family, 'titleGrammar': family.get('titleGrammar', 'Use the selected measured title cadence.'),
                          'roleGrammar': family.get('narrativeSlots', family.get('narrative', {}).get('roles', [])),
                          'compositionStatus': 'Fixed approved layout; language does not reopen family selection.'})
            selected_copy = None
            for copy_file in sorted((REF / 'author-examples').glob('focused-copy-*.json')):
                records = read_json(copy_file).get('families', [])
                matches = [x for x in records if x['family'] == a.family]
                if matches:
                    if selected_copy is not None:
                        ap.error('duplicate selected copy-family record')
                    selected_copy = {k: v for k, v in matches[0].items() if k != 'sourceVerbatim'}
            if selected_copy:
                style.update(selected_copy)
                style['scope'] = 'Selected language evidence only. Source facts are not current science; do not copy source errors or claims.'
        write_json(dst / 'copy-style.json', style)
        files.append('copy-style.json')
    else:
        doc('local-pptx.md' if a.backend == 'pptx' else 'google-slides.md', 'backend.md')
        doc('author-components.md', 'native-components.md')
        (dst / 'native-module-path.txt').write_text(str(ROOT / 'scripts/author_components.mjs'), encoding='utf-8')
        files.append('native-module-path.txt')
    if a.stage == 'layout':
        targets = {'../recovery-contract.md': 'recovery-contract.md',
                   '../layout/family-selector.md': 'family-selector.md',
                   'family-selector.md': 'family-selector.md',
                   '../author-profile.md': 'brand-invariants.json',
                   '../author-style-execution.md': 'layout-style.json',
                   '../author-examples/author-family-layouts.json': 'layout-style.json',
                   '../author-examples/focused-layout-starters.json': 'layout-style.json',
                   '../author-examples/index.md': 'style-reference.png',
                   '../layout/' + a.specialist + '.md': 'specialist.md',
                   a.specialist + '.md': 'specialist.md'}
        if focused_module:
            targets.update({'../layout/' + focused_module + '.md': 'focused-specialist.md',
                            focused_module + '.md': 'focused-specialist.md'})
        if table_component:
            targets.update({'../layout/scientific-table.md': 'table-component.md',
                            'scientific-table.md': 'table-component.md'})
        for name in ('stage-guide.md', 'family-selector.md', 'specialist.md', 'focused-specialist.md', 'table-component.md'):
            if (dst / name).is_file():
                localize_links(dst / name, targets)
    elif a.stage == 'copy':
        targets = {'../recovery-contract.md': 'recovery-contract.md', '../copy/working-language.md': 'working-language.md',
                   '../copy/title.md': 'title.md', '../copy/' + choice + '.md': 'specialist.md'}
        if procedure_guide:
            targets.update({'../copy/method-procedure.md': 'procedure-guide.md',
                            'method-procedure.md': 'procedure-guide.md'})
        for name in ('stage-guide.md', 'working-language.md', 'title.md', 'specialist.md', 'procedure-guide.md'):
            if (dst / name).is_file():
                localize_links(dst / name, targets)
    write_json(dst / 'facts.json', facts)
    files.append('facts.json')
    for name, source in [('layout.json', a.layout), ('copy.json', a.copy)]:
        if source and (a.stage == 'assembly' or (name == 'layout.json' and a.stage == 'copy')):
            write_json(dst / name, approved_plan(read_json(source)) if name == 'layout.json' else read_json(source))
            files.append(name)
    if selection_decision:
        write_json(dst / 'selection.json', selection_decision)
        files.append('selection.json')
    manifest = {'stage': a.stage, 'caseId': facts.get('caseId'), 'specialist': a.specialist,
                'example': example, 'family': a.family, 'files': files,
                'candidateExamples': a.candidates,
                'originalFactsSha256': hashlib.sha256(Path(a.facts).read_bytes()).hexdigest(),
                'scientificEvidence': evidence_map,
                'fileSha256': {name: hashlib.sha256((dst / name).read_bytes()).hexdigest() for name in files},
                'scope': 'Only this packet plus required host docs/runtime. Reference links in copied guides do not authorize reading unrelated guides. Request missing stage material upstream.'}
    write_json(dst / 'packet-manifest.json', manifest)
    print(json.dumps({'packet': str(dst), 'stage': a.stage, 'files': files}))


if __name__ == '__main__':
    main()
