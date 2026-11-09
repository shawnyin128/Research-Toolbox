#!/usr/bin/env python3
"""Validate local recovery plans and literal witnesses; never claim scientific entailment."""
import argparse
import json
import re
from pathlib import Path

ROLES = {'goal', 'observation', 'interpretation', 'setup', 'pending',
         'symbol_definition', 'evidence_embedded', 'audience_context', 'maker_guardrail'}
PUBLIC = {'recoverable', 'visible_text', 'visible_label', 'evidence_only'}
DELIVERIES = PUBLIC | {'context_only', 'private'}
ALLOWED = {
    **{r: PUBLIC for r in ('goal', 'observation', 'interpretation', 'setup', 'pending')},
    'symbol_definition': {'recoverable', 'visible_text', 'visible_label', 'context_only'},
    'evidence_embedded': {'recoverable', 'evidence_only'},
    'audience_context': {'context_only'}, 'maker_guardrail': {'private'},
}
KINDS = {'title', 'header', 'table', 'math', 'diagram', 'asset', 'prose', 'label'}


class ContractError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ContractError(message)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def validate_facts(data):
    require(isinstance(data, dict) and data.get('schemaVersion') == 2,
            'facts must use schemaVersion 2; old paragraph contracts require semantic extraction')
    require(nonempty(data.get('caseId')), 'caseId required')
    records = data.get('facts')
    require(isinstance(records, list) and records, 'facts must be a nonempty list')
    evidence = {}
    for kind in ('tables', 'assets'):
        require(isinstance(data.get(kind), list), f'{kind} must be a separate list')
        for item in data[kind]:
            require(isinstance(item, dict) and nonempty(item.get('id')), f'{kind} item needs id')
            require(item['id'] not in evidence, 'evidence ids must be unique')
            require(nonempty(item.get('source')), f"{item['id']}: evidence source required")
            evidence[item['id']] = item
            if kind == 'tables':
                cols, rows = item.get('columns'), item.get('rows')
                require(isinstance(cols, list) and cols and all(isinstance(x, str) for x in cols),
                        f"{item['id']}: exact string columns required")
                require(isinstance(rows, list) and rows and all(isinstance(row, list) and len(row) == len(cols)
                        and all(isinstance(x, str) for x in row) for row in rows),
                        f"{item['id']}: exact string rows must match columns")
                metadata = item.get('columnMetadata', [])
                require(isinstance(metadata, list), 'columnMetadata must be a list')
                indices = set()
                for col in metadata:
                    require(isinstance(col, dict), 'column metadata must be an object')
                    i = col.get('columnIndex')
                    require(type(i) is int and 0 <= i < len(cols) and i not in indices,
                            'columnMetadata needs unique valid columnIndex')
                    require(nonempty(col.get('meaning')), 'column metadata meaning required')
                    require('unit' not in col or nonempty(col['unit']), 'column unit must be a string')
                    indices.add(i)
            else:
                require(nonempty(item.get('path')), f"{item['id']}: asset path required")
                digest = item.get('sha256')
                require(isinstance(digest, str) and re.fullmatch('[0-9a-f]{64}', digest),
                        f"{item['id']}: sha256 required")
    equations = data.get('equations', [])
    require(isinstance(equations, list), 'equations must be a list')
    equation_ids = set()
    for equation in equations:
        require(isinstance(equation, dict) and nonempty(equation.get('id')) and
                equation['id'] not in equation_ids and nonempty(equation.get('source')) and
                nonempty(equation.get('expression')), 'equation needs unique id, source and expression')
        definitions = equation.get('definitions', [])
        require(isinstance(definitions, list) and all(isinstance(d, dict) and
                nonempty(d.get('symbol')) and nonempty(d.get('meaning')) for d in definitions),
                'equation definitions need symbol and meaning')
        equation_ids.add(equation['id'])
    ids = set()
    for fact in records:
        require(isinstance(fact, dict), 'each fact must be an object')
        fid = fact.get('id')
        require(nonempty(fid) and fid not in ids, 'fact ids must be nonempty and unique')
        ids.add(fid)
        role, delivery = fact.get('role'), fact.get('delivery')
        require(isinstance(role, str) and role in ROLES, f'{fid}: invalid/missing role')
        require(isinstance(delivery, str) and delivery in ALLOWED[role], f'{fid}: invalid delivery for {role}')
        require('visibility' not in fact, f'{fid}: vague visibility fields are not a delivery contract')
        require(nonempty(fact.get('statement')) and nonempty(fact.get('source')),
                f'{fid}: atomic statement and source locator required')
        if delivery == 'evidence_only':
            require(nonempty(fact.get('evidenceRef')) and fact['evidenceRef'] in evidence and nonempty(fact.get('locator')),
                    f'{fid}: evidence_only requires a known evidenceRef and exact locator')
        if role == 'symbol_definition':
            require(nonempty(fact.get('symbol')) and nonempty(fact.get('meaning')),
                    f'{fid}: symbol and canonical meaning required')
            require(isinstance(fact.get('essential'), bool), f'{fid}: essential must be boolean')
            prior = fact.get('priorDefinition')
            if prior is not None:
                require(isinstance(prior, dict) and nonempty(prior.get('source')) and nonempty(prior.get('location')),
                        f'{fid}: prior definition needs explicit source and location')
            if delivery == 'context_only':
                require(prior is not None, f'{fid}: context_only symbol requires a specific prior definition')
            if fact['essential'] and prior is None:
                require(delivery in PUBLIC, f'{fid}: essential new symbol must be recoverable')
    return data


def slot_text(slot):
    require(isinstance(slot, dict), 'copy slot must be an object')
    paragraphs = slot.get('paragraphs')
    if paragraphs is not None:
        require(isinstance(paragraphs, list), 'paragraphs must be a list')
        lines = []
        for p in paragraphs:
            require(isinstance(p, dict) and isinstance(p.get('runs'), list), 'paragraph runs required')
            require(all(isinstance(r, dict) and isinstance(r.get('text'), str) for r in p['runs']), 'each run needs text')
            lines.append(''.join(r['text'] for r in p['runs']))
        rendered = '\n'.join(lines)
        if 'text' in slot:
            require(slot['text'] == rendered, 'slot text disagrees with paragraph/run text')
        return rendered
    require(isinstance(slot.get('text'), str), 'copy slot needs text or native paragraph runs')
    return slot['text']


def planned_slots(layout):
    raw = layout.get('slots')
    require(isinstance(raw, (dict, list)), 'layout slots must be a list or object')
    if isinstance(raw, dict):
        require(all(nonempty(k) and isinstance(v, dict) for k, v in raw.items()), 'invalid layout slots')
        return set(raw)
    require(all(isinstance(s, dict) and nonempty(s.get('id')) for s in raw), 'layout slot needs stable id')
    ids = [s['id'] for s in raw]
    require(len(ids) == len(set(ids)), 'layout slot ids must be unique')
    return set(ids)


def evidence_locator(item, locator):
    require(nonempty(locator), 'evidenceLocator required')
    if 'columns' not in item:  # Asset regions are checked independently on the actual saved page.
        return
    if locator == 'whole':
        return
    match = re.fullmatch(r'columns\[(\d+)\]|rows\[(\d+)\]\[(\d+)\]', locator)
    require(match is not None, 'table evidenceLocator must be whole, columns[N], or rows[R][C]')
    if match[1] is not None:
        require(int(match[1]) < len(item['columns']), 'table column locator out of range')
    else:
        require(int(match[2]) < len(item['rows']) and int(match[3]) < len(item['columns']), 'table cell locator out of range')


def evidence_text(item, locator):
    """Exact table strings can witness local definitions without duplicated copy."""
    if 'columns' not in item or locator == 'whole':
        return ''
    match = re.fullmatch(r'columns\[(\d+)\]|rows\[(\d+)\]\[(\d+)\]', locator)
    if match[1] is not None:
        return item['columns'][int(match[1])]
    return item['rows'][int(match[2])][int(match[3])]


def witness_key(w):
    return tuple(w.get(k) for k in ('objectId', 'locator', 'slotId', 'evidenceLocator'))


def validate_layout(facts, layout):
    validate_facts(facts)
    require(isinstance(layout, dict) and layout.get('stage') == 'layout' and
            layout.get('caseId') == facts['caseId'], 'same-case layout-stage contract required')
    slots = planned_slots(layout)
    has_plan = 'objects' in layout or 'recovery' in layout
    require(has_plan or not any(f['delivery'] == 'recoverable' for f in facts['facts']),
            'recoverable obligations require layout objects and recovery map')
    if not has_plan:  # Existing explicit-delivery v2 plans remain readable.
        return layout
    objects, recovery = layout.get('objects'), layout.get('recovery')
    require(isinstance(objects, list) and isinstance(recovery, list), 'layout objects and recovery lists required')
    objs = {}
    evidence = {e['id']: e for e in facts['tables'] + facts['assets']}
    known = {f['id']: f for f in facts['facts']}
    for obj in objects:
        require(isinstance(obj, dict) and nonempty(obj.get('id')) and obj['id'] not in objs, 'unique object id required')
        require(obj.get('kind') in KINDS and nonempty(obj.get('locator')), 'object kind and page locator required')
        if 'slotId' in obj:
            require(obj['slotId'] in slots, 'object references unknown layout slot')
        if 'evidenceRef' in obj:
            require(obj['evidenceRef'] in evidence, 'object references unknown evidence')
        require(not ('slotId' in obj and 'text' in obj), 'copy-owned objects cannot freeze duplicate text')
        objs[obj['id']] = obj
    seen = set()
    for entry in recovery:
        require(isinstance(entry, dict), 'recovery entry must be an object')
        fid = entry.get('factId')
        require(fid in known and fid not in seen, 'recovery needs unique known factId')
        fact = known[fid]
        require(fact['delivery'] in PUBLIC, f'{fid}: private/context facts cannot enter recovery')
        ws = entry.get('witnesses')
        require(isinstance(ws, list) and ws, f'{fid}: nonempty recovery witnesses required')
        keys = set()
        for w in ws:
            require(isinstance(w, dict) and w.get('objectId') in objs, f'{fid}: unknown recovery object')
            obj = objs[w['objectId']]
            require(w.get('locator') == obj['locator'], f'{fid}: witness must locate the planned object')
            require(w.get('slotId') == obj.get('slotId'), f'{fid}: witness must use actual planned slot')
            if 'slotId' not in obj:
                require('evidenceRef' in obj or nonempty(obj.get('text')), 'non-slot recovery needs frozen object text or evidence')
            if 'evidenceRef' in obj:
                evidence_locator(evidence[obj['evidenceRef']], w.get('evidenceLocator'))
            else:
                require('evidenceLocator' not in w, 'non-evidence object cannot claim evidence locator')
            if fact['delivery'] == 'evidence_only':
                require(obj.get('evidenceRef') == fact['evidenceRef'], f'{fid}: evidence_only must retain frozen evidenceRef')
            if fact['delivery'] in {'visible_text', 'visible_label'}:
                require('slotId' in obj or nonempty(obj.get('text')), f'{fid}: explicit text obligation needs actual text surface')
            if fact['delivery'] == 'visible_label':
                require(obj['kind'] in {'label', 'header', 'math', 'diagram'}, f'{fid}: explicit label obligation needs label object')
            require(witness_key(w) not in keys, 'duplicate recovery witness')
            keys.add(witness_key(w))
        seen.add(fid)
    required = {f['id'] for f in facts['facts'] if f['delivery'] in PUBLIC}
    require(required == seen, f'missing public recovery plan: {sorted(required - seen)}')
    return layout


def span_text(quote, span, label):
    require(isinstance(span, list) and len(span) == 2 and all(type(x) is int for x in span)
            and 0 <= span[0] < span[1] <= len(quote), f'{label}: valid visible span required')
    return quote[span[0]:span[1]]


def check_mapping(fact, quotes, mapping, canonical=False):
    require(isinstance(mapping, dict), f"{fact['id']}: symbol mapping witness required")
    si, mi = mapping.get('symbolWitness', 0), mapping.get('meaningWitness', 0)
    require(type(si) is int and type(mi) is int and 0 <= si < len(quotes) and 0 <= mi < len(quotes), 'mapping witness index invalid')
    ss, ms = mapping.get('symbolSpan'), mapping.get('meaningSpan')
    require(span_text(quotes[si], ss, 'symbolSpan') == fact['symbol'], 'symbolSpan must locate exact symbol')
    meaning = span_text(quotes[mi], ms, 'meaningSpan')
    require(meaning.strip() and meaning != fact['symbol'], 'meaningSpan needs a distinct visible meaning')
    if canonical:
        require(meaning == fact['meaning'], 'legacy meaningSpan must locate canonical literal')
    if si == mi:
        require(ss[1] <= ms[0] or ms[1] <= ss[0], 'symbol and meaning spans must be distinct, not a hidden letter')
    # A letter inside an unrelated word cannot masquerade as the local symbol.
    for at in (ss[0] - 1, ss[1]):
        require(at < 0 or at >= len(quotes[si]) or not quotes[si][at].isalnum(), 'symbol must be a separate visible token')


def validate_copy(facts, copy, layout=None):
    validate_facts(facts)
    require(isinstance(copy, dict) and copy.get('schemaVersion') == 2, 'copy requires schemaVersion 2')
    require(copy.get('caseId') == facts['caseId'], 'copy/facts caseId mismatch')
    slots = copy.get('slots')
    require(isinstance(slots, dict), 'copy slots must be keyed by approved slot ids')
    text = {sid: slot_text(s) for sid, s in slots.items()}
    known = {f['id']: f for f in facts['facts']}
    if layout is not None:
        validate_layout(facts, layout)
        require(set(slots) <= planned_slots(layout), 'copy contains unplanned slot')
    require(layout is not None or not any(f['delivery'] == 'recoverable' for f in facts['facts']), 'recoverable copy requires --layout')
    for sid, slot in slots.items():
        require(isinstance(slot.get('factIds', []), list), 'slot factIds must be a list')
        for fid in slot.get('factIds', []):
            require(fid in known and known[fid]['delivery'] in PUBLIC - {'evidence_only'}, f'{sid}: unknown/private/context/evidence-only fact in copy')
    coverage = copy.get('coverage')
    require(isinstance(coverage, list), 'coverage witnesses required; factIds alone do not establish recovery')
    if layout is not None and 'recovery' in layout:
        objs = {o['id']: o for o in layout['objects']}
        evidence = {e['id']: e for e in facts['tables'] + facts['assets']}
        plans = {p['factId']: p for p in layout['recovery']}
        seen = set()
        for entry in coverage:
            require(isinstance(entry, dict) and entry.get('factId') in plans, 'coverage needs planned public factId')
            fid = entry['factId']
            require(fid not in seen, 'duplicate fact coverage')
            ws = entry.get('witnesses')
            require(isinstance(ws, list) and len(ws) == len(plans[fid]['witnesses']), f'{fid}: actual witnesses must cover full joint recovery plan')
            require({witness_key(w) for w in ws} == {witness_key(w) for w in plans[fid]['witnesses']}, f'{fid}: coverage differs from planned slots/evidence')
            quotes = []
            for w in ws:
                obj = objs[w['objectId']]
                if 'slotId' in obj or 'text' in obj:
                    sid = obj.get('slotId')
                    require(sid is None or sid in text, f'{fid}: missing actual planned slot text')
                    actual = text[sid] if sid else obj['text']
                    quote = w.get('quote')
                    require(nonempty(quote) and quote in actual, f'{fid}: quote must occur on actual planned text surface')
                    if sid:
                        require(fid in slots[sid].get('factIds', []), f'{fid}: missing slot factIds link')
                    quotes.append(quote)
                else:
                    require('quote' not in w, 'asset/table evidence must use precise evidenceLocator, not invented quote')
                    quotes.append(evidence_text(evidence[obj['evidenceRef']], w['evidenceLocator']))
            if known[fid]['role'] == 'symbol_definition' and known[fid].get('priorDefinition') is None:
                mapping = entry.get('mapping')
                if isinstance(mapping, dict) and 'evidenceWitness' in mapping:
                    index = mapping['evidenceWitness']
                    require(type(index) is int and 0 <= index < len(ws), 'mapping evidence witness index invalid')
                    obj = objs[ws[index]['objectId']]
                    item = evidence.get(obj.get('evidenceRef'), {})
                    require('path' in item and ws[index].get('evidenceLocator') not in {'whole', 'entire asset'},
                            'asset mapping needs a precise planned definition region')
                else:
                    check_mapping(known[fid], quotes, mapping)
            seen.add(fid)
        require(seen == set(plans), f'missing recovery witnesses: {sorted(set(plans) - seen)}')
        for sid, slot in slots.items():
            permitted = {fid for fid, p in plans.items() if any(w.get('slotId') == sid for w in p['witnesses'])}
            require(set(slot.get('factIds', [])) <= permitted, f'{sid}: unplanned fact assignment')
    else:
        seen = set()
        for witness in coverage:
            require(isinstance(witness, dict), 'coverage witness must be an object')
            fid, sid = witness.get('factId'), witness.get('slotId')
            require(fid in known and sid in text, 'coverage needs known factId and slotId')
            fact, quote = known[fid], witness.get('quote')
            require(fact['delivery'] in {'visible_text', 'visible_label'}, f'{fid}: not a text/label obligation')
            require(nonempty(quote) and quote in text[sid], f'{fid}: quote must occur in actual slot text')
            require(fid in slots[sid].get('factIds', []), f'{fid}: missing slot factIds link')
            if fact['role'] == 'symbol_definition':
                check_mapping(fact, [quote], witness, canonical=True)
            seen.add(fid)
        required = {f['id'] for f in facts['facts'] if f['delivery'] in {'visible_text', 'visible_label'}}
        require(required <= seen, f'missing visible coverage witnesses: {sorted(required - seen)}')
    return copy


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('facts')
    ap.add_argument('--layout')
    ap.add_argument('--copy')
    a = ap.parse_args()
    try:
        facts = json.loads(Path(a.facts).read_text(encoding='utf-8'))
        validate_facts(facts)
        layout = json.loads(Path(a.layout).read_text(encoding='utf-8')) if a.layout else None
        if layout is not None:
            validate_layout(facts, layout)
        if a.copy:
            validate_copy(facts, json.loads(Path(a.copy).read_text(encoding='utf-8')), layout)
    except (ContractError, ValueError, OSError, TypeError, KeyError) as e:
        ap.exit(1, f'REJECTED: {e}\n')
    print('PASS: structure and actual literal witnesses only; independent rendered-page science review required')


if __name__ == '__main__':
    main()
