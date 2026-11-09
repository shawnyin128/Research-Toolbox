#!/usr/bin/env python3
"""Generic toy smoke checks. No held-out science or source slides are read."""
import json
import copy as deepcopy_module
import re
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from validate_contracts import ContractError, validate_facts, validate_layout, validate_copy

ROOT = Path(__file__).resolve().parents[1]
_SCRATCH = tempfile.TemporaryDirectory(prefix='research-slides-contracts-')
WORK = Path(_SCRATCH.name)


def toy():
    return {'schemaVersion': 2, 'caseId': 'toy-routing', 'audience': 'project collaborators',
            'selection': {'footer': 'nyu'}, 'facts': [
                {'id': 'purpose', 'role': 'goal', 'statement': 'Cedar refines routing costs.',
                 'source': 'toy notes: line 1', 'delivery': 'visible_text'},
                {'id': 'result', 'role': 'observation',
                 'statement': 'Cedar has the lowest error among the tested compressed variants.',
                 'source': 'toy notes: line 2', 'delivery': 'visible_text'},
                {'id': 'meaning', 'role': 'symbol_definition', 'symbol': 'r', 'meaning': 'recent tokens',
                 'essential': True, 'statement': 'r denotes recent tokens.',
                 'source': 'toy notes: line 3', 'delivery': 'visible_label'},
                {'id': 'status', 'role': 'pending', 'statement': 'The wider routing trial is pending.',
                 'source': 'toy notes: line 4', 'delivery': 'visible_text'},
                {'id': 'guard', 'role': 'maker_guardrail', 'statement': 'Use only the supplied measured values.',
                 'source': 'toy notes: line 5', 'delivery': 'private'},
                {'id': 'embedded', 'role': 'evidence_embedded', 'statement': 'The tested batch has four items.',
                 'source': 'toy table: row 1', 'delivery': 'evidence_only', 'evidenceRef': 'values',
                 'locator': 'row Cedar; column Batch'},
                {'id': 'context', 'role': 'audience_context', 'statement': 'The audience is the routing team.',
                 'source': 'toy notes: heading', 'delivery': 'context_only'}],
            'tables': [{'id': 'values', 'source': 'toy notes: table', 'columns': ['Method', 'Batch', 'Error'],
                        'rows': [['Cedar', '4', '0.20'], ['Reference', 'NA', '0.30']]}], 'assets': []}


def toy_copy(facts):
    visible = [f for f in facts['facts'] if f['delivery'] in {'visible_text', 'visible_label'}]
    result = {'schemaVersion': 2, 'caseId': facts['caseId'],
            'slots': {f['id']: {'text': f['statement'], 'factIds': [f['id']]} for f in visible},
            'coverage': [{'factId': f['id'], 'slotId': f['id'], 'quote': f['statement']} for f in visible]}
    for f, witness in zip(visible, result['coverage']):
        if f['role'] == 'symbol_definition':
            start = witness['quote'].index(f['symbol'])
            meaning_start = witness['quote'].index(f['meaning'])
            witness.update(symbolSpan=[start, start + len(f['symbol'])],
                           meaningSpan=[meaning_start, meaning_start + len(f['meaning'])])
    return result


class Contracts(unittest.TestCase):
    def setUp(self):
        self.facts = toy()
        self.copy = toy_copy(self.facts)

    def reject_fact(self, mutate):
        mutate(self.facts)
        with self.assertRaises(ContractError):
            validate_facts(self.facts)

    def test_positive_scientific_status_and_private_guard(self):
        validate_copy(self.facts, self.copy)
        self.assertIn('pending', self.copy['slots']['status']['text'])
        self.assertNotIn('guard', self.copy['slots'])

    def test_reject_flat_paragraph_visibility(self):
        self.facts = {'caseId': 'old', 'facts': [{'id': 'F1', 'text': 'Several combined claims.',
                     'visibility': 'scientific content visible as required; maker guards private'}]}
        self.reject_fact(lambda f: None)

    def test_reject_unknown_role(self):
        self.reject_fact(lambda f: f['facts'][0].update(role='research_info'))

    def test_reject_vague_delivery(self):
        self.reject_fact(lambda f: f['facts'][0].update(delivery='visible as required'))

    def test_reject_visible_guardrail(self):
        self.reject_fact(lambda f: f['facts'][4].update(delivery='visible_text'))

    def test_reject_new_symbol_as_context(self):
        self.reject_fact(lambda f: f['facts'][2].update(delivery='context_only'))

    def test_explicit_prior_definition(self):
        self.facts['facts'][2].update(delivery='context_only',
            priorDefinition={'source': 'preceding project page', 'location': 'routing diagram legend'})
        validate_copy(self.facts, toy_copy(self.facts))

    def test_reject_numeric_table_cell(self):
        self.reject_fact(lambda f: f['tables'][0]['rows'][0].__setitem__(2, 0.2))

    def test_reject_embedded_without_locator(self):
        self.reject_fact(lambda f: f['facts'][5].pop('locator'))

    def test_reject_fact_ids_without_witness(self):
        self.copy.pop('coverage')
        with self.assertRaises(ContractError):
            validate_copy(self.facts, self.copy)

    def test_reject_bare_symbol_recovery(self):
        self.copy['slots']['meaning']['text'] = 'r'
        self.copy['coverage'][2]['quote'] = 'r'
        with self.assertRaises(ContractError):
            validate_copy(self.facts, self.copy)

    def test_reject_symbol_hidden_inside_meaning(self):
        self.copy['slots']['meaning']['text'] = 'recent tokens'
        self.copy['coverage'][2].update(quote='recent tokens', symbolSpan=[0, 1], meaningSpan=[0, 13])
        with self.assertRaises(ContractError):
            validate_copy(self.facts, self.copy)

    def test_reject_nonexistent_quote(self):
        self.copy['coverage'][1]['quote'] = 'The result is certain for all variants.'
        with self.assertRaises(ContractError):
            validate_copy(self.facts, self.copy)

    def test_reject_private_copy_link(self):
        self.copy['slots']['result']['factIds'].append('guard')
        with self.assertRaises(ContractError):
            validate_copy(self.facts, self.copy)

    def test_reject_divergent_native_run_text(self):
        self.copy['slots']['meaning']['paragraphs'] = [{'runs': [{'text': 'r'}]}]
        with self.assertRaises(ContractError):
            validate_copy(self.facts, self.copy)

    def test_semantic_error_requires_review(self):
        # This deliberately false sentence passes structural checks. The gate makes no
        # semantic claim: a reviewer must reject the lost scope despite a real quote/id.
        self.copy['slots']['result']['text'] = 'Cedar is best in every situation.'
        self.copy['coverage'][1]['quote'] = 'Cedar is best in every situation.'
        validate_copy(self.facts, self.copy)


def joint_toy():
    facts = {'schemaVersion': 2, 'caseId': 'joint-toy', 'audience': 'internal ML collaborators',
        'selection': {'footer': 'nyu'}, 'facts': [
        {'id': 'comparison', 'role': 'observation', 'delivery': 'recoverable',
         'statement': 'Cedar error is lower than Reference on the tested batch.', 'source': 'toy record table'},
        {'id': 'mapping', 'role': 'symbol_definition', 'delivery': 'recoverable', 'symbol': 'S',
         'meaning': 'sink window', 'essential': True, 'statement': 'S denotes the sink window.', 'source': 'toy record key'},
        {'id': 'math', 'role': 'symbol_definition', 'delivery': 'recoverable', 'symbol': 'z',
         'meaning': 'sum of x and y', 'essential': True, 'statement': 'z is the sum of x and y.', 'source': 'toy equation'},
        {'id': 'guard', 'role': 'maker_guardrail', 'delivery': 'private', 'statement': 'Do not extrapolate.', 'source': 'toy constraint'},
        {'id': 'context', 'role': 'audience_context', 'delivery': 'context_only', 'statement': 'BF16 is familiar.', 'source': 'toy audience'}],
        'tables': [{'id': 'values', 'source': 'toy table', 'columns': ['Method', 'Error'],
                    'rows': [['Cedar', '0.20'], ['Reference', '0.30'], ['Unknown', 'NA']],
                    'columnMetadata': [{'columnIndex': 1, 'meaning': 'measured error', 'unit': 'dimensionless', 'direction': 'lower is better'}]}],
        'equations': [{'id': 'sum', 'source': 'toy equation', 'expression': 'z := x + y',
                       'definitions': [{'symbol': 'z', 'meaning': 'sum of x and y'}]}], 'assets': []}
    layout = {'schemaVersion': 2, 'stage': 'layout', 'caseId': facts['caseId'],
        'slots': [{'id': 'title'}, {'id': 'key'}],
        'objects': [{'id': 'topic', 'kind': 'title', 'locator': 'top', 'slotId': 'title'},
                    {'id': 'table', 'kind': 'table', 'locator': 'lower', 'evidenceRef': 'values'},
                    {'id': 'key', 'kind': 'label', 'locator': 'near object', 'slotId': 'key'},
                    {'id': 'eq', 'kind': 'math', 'locator': 'center', 'text': 'z := x + y'}],
        'recovery': [
            {'factId': 'comparison', 'witnesses': [{'objectId': 'topic', 'locator': 'top', 'slotId': 'title'},
                                                 {'objectId': 'table', 'locator': 'lower', 'evidenceLocator': 'whole'},
                                                 {'objectId': 'table', 'locator': 'lower', 'evidenceLocator': 'columns[1]'}]},
            {'factId': 'mapping', 'witnesses': [{'objectId': 'key', 'locator': 'near object', 'slotId': 'key'}]},
            {'factId': 'math', 'witnesses': [{'objectId': 'eq', 'locator': 'center'}]}]}
    copy = {'schemaVersion': 2, 'caseId': facts['caseId'],
        'slots': {'title': {'text': 'Cedar: tested batch', 'factIds': ['comparison']},
                  'key': {'text': 'Sink(S)', 'factIds': ['mapping']}},
        'coverage': deepcopy_module.deepcopy(layout['recovery'])}
    copy['coverage'][0]['witnesses'][0]['quote'] = 'Cedar: tested batch'
    copy['coverage'][1]['witnesses'][0]['quote'] = 'Sink(S)'
    copy['coverage'][1]['mapping'] = {'symbolWitness': 0, 'symbolSpan': [5,6], 'meaningWitness': 0, 'meaningSpan': [0,4]}
    copy['coverage'][2]['witnesses'][0]['quote'] = 'z := x + y'
    copy['coverage'][2]['mapping'] = {'symbolWitness': 0, 'symbolSpan': [0,1], 'meaningWitness': 0, 'meaningSpan': [5,10]}
    return facts, layout, copy


class Recovery(unittest.TestCase):
    def setUp(self):
        self.facts, self.layout, self.copy = joint_toy()

    def test_joint_title_header_exact_table_and_formal_math_without_prose(self):
        validate_copy(self.facts, self.copy, self.layout)
        self.assertEqual(self.facts['tables'][0]['rows'][0][1], '0.20')
        self.assertEqual(self.facts['tables'][0]['rows'][2][1], 'NA')
        self.assertEqual(len(self.copy['slots']), 2)

    def test_reject_recoverable_without_layout(self):
        with self.assertRaises(ContractError): validate_copy(self.facts, self.copy)

    def test_missing_or_changed_planned_surfaces_and_evidence(self):
        mutations = [lambda l,c: l['recovery'].pop(),
            lambda l,c: l['recovery'][0]['witnesses'][0].update(slotId='missing'),
            lambda l,c: l['objects'][1].update(evidenceRef='missing'),
            lambda l,c: c['coverage'][0]['witnesses'].pop(),
            lambda l,c: c['coverage'][0]['witnesses'][1].update(evidenceLocator='columns[1]'),
            lambda l,c: c['coverage'][0]['witnesses'][0].update(quote='nonexistent'),
            lambda l,c: c['slots'].pop('title'),
            lambda l,c: c['slots'].update(extra={'text':'Unplanned claim', 'factIds':[]}),
            lambda l,c: c['coverage'][1].pop('mapping'),
            lambda l,c: l['recovery'][0]['witnesses'][1].update(evidenceLocator='rows[9][1]')]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                l,c = deepcopy_module.deepcopy(self.layout),deepcopy_module.deepcopy(self.copy)
                mutate(l,c)
                with self.assertRaises(ContractError): validate_copy(self.facts,c,l)

    def test_explicit_text_cannot_disappear_into_table(self):
        self.facts['facts'][0]['delivery'] = 'visible_text'
        self.layout['recovery'][0]['witnesses'] = [self.layout['recovery'][0]['witnesses'][1]]
        with self.assertRaises(ContractError): validate_layout(self.facts,self.layout)

    def test_private_context_and_unplanned_fact_assignments(self):
        for fid in ('guard','context','math'):
            c = deepcopy_module.deepcopy(self.copy)
            c['slots']['title']['factIds'].append(fid)
            with self.assertRaises(ContractError): validate_copy(self.facts,c,self.layout)
        self.layout['recovery'].append({'factId':'guard','witnesses':self.layout['recovery'][0]['witnesses']})
        with self.assertRaises(ContractError): validate_layout(self.facts,self.layout)

    def test_new_symbol_hidden_letter_is_not_definition(self):
        self.copy['slots']['key']['text'] = 'Sinking'
        self.copy['coverage'][1]['witnesses'][0]['quote'] = 'Sinking'
        self.copy['coverage'][1]['mapping'].update(symbolSpan=[0,1], meaningSpan=[1,7])
        with self.assertRaises(ContractError): validate_copy(self.facts,self.copy,self.layout)

    def test_existing_asset_definition_and_table_header_need_no_duplicate_label(self):
        for surface in ('asset', 'table'):
            f,l,c = joint_toy()
            label = l['objects'][2]
            label.pop('slotId')
            planned = l['recovery'][1]['witnesses'][0]
            planned.pop('slotId')
            if surface == 'asset':
                f['assets'] = [{'id':'diagram','source':'toy figure','path':'diagram.png','sha256':'a'*64}]
                label.update(kind='asset',evidenceRef='diagram')
                planned['evidenceLocator'] = 'upper left paired Sink(S) label'
                mapping = {'evidenceWitness':0}
            else:
                f['tables'][0]['columns'][0] = 'Sink(S)'
                label.update(kind='table',evidenceRef='values')
                planned['evidenceLocator'] = 'columns[0]'
                mapping = {'symbolWitness':0,'symbolSpan':[5,6],'meaningWitness':0,'meaningSpan':[0,4]}
            c['slots'].pop('key')
            c['coverage'][1] = deepcopy_module.deepcopy(l['recovery'][1])
            c['coverage'][1]['mapping'] = mapping
            validate_copy(f,c,l)
            c['coverage'][1]['witnesses'][0]['quote'] = 'invented asset quotation'
            with self.assertRaises(ContractError): validate_copy(f,c,l)

    def test_typed_metadata_is_not_a_prose_fact(self):
        validate_layout(self.facts,self.layout)
        self.assertNotIn('dimensionless', str(self.copy))
        self.facts['tables'][0]['columnMetadata'][0]['columnIndex'] = 99
        with self.assertRaises(ContractError): validate_facts(self.facts)


class Packets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        WORK.mkdir(parents=True, exist_ok=True)
        cls.temp = tempfile.TemporaryDirectory(prefix='smoke-', dir=WORK)
        cls.base = Path(cls.temp.name)
        cls.facts = toy()
        cls.facts['rawNotes'] = 'UPSTREAM ONLY: mixed raw source archive'
        cls.f = cls.base / 'facts.json'
        cls.f.write_text(json.dumps(cls.facts))
        cls.layout = cls.base / 'layout.json'
        cls.layout.write_text(json.dumps({'caseId': 'toy-routing', 'stage': 'layout', 'slots': []}))

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def build(self, stage, name, extra=()):
        return subprocess.run([sys.executable, str(ROOT / 'scripts/make_stage_packet.py'), stage,
            '--facts', str(self.f), '--specialist', 'mechanism', '--out', str(self.base / name), *extra],
            text=True, capture_output=True)

    def test_copy_title_evidence_and_stage_separation(self):
        for example in (1, 10, 11):
            result = self.build('copy', f'copy-{example}', ['--layout', str(self.layout), '--example', str(example)])
            self.assertEqual(result.returncode, 0, result.stderr)
            packet = self.base / f'copy-{example}'
            style = json.loads((packet / 'copy-style.json').read_text())
            self.assertEqual(style['example'], f'example-{example:02d}.png')
            self.assertTrue(style['titleEvidence']['actualText'])
            self.assertIn('bodyEvidence', style)
            self.assertFalse((packet / 'style-reference.png').exists())
            self.assertFalse((packet / 'brand-invariants.json').exists())
            self.assertNotIn('rawNotes', json.loads((packet / 'facts.json').read_text()))

    def assert_local_links_resolve(self, packet):
        for guide in packet.glob('*.md'):
            for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', guide.read_text()):
                self.assertTrue((packet / target).is_file(), f'{guide.name}: missing local link {target}')

    def test_all_recorded_examples_build_layout_and_copy(self):
        for entry in json.loads((ROOT / 'references/author-examples/family-inventory.json').read_text())['families']:
            example = int(entry['exampleId'].split('-')[1])
            for stage in ('layout', 'copy'):
                with self.subTest(example=example, stage=stage):
                    extra = ['--example', str(example)]
                    if stage == 'copy':
                        extra.extend(['--layout', str(self.layout)])
                    name = f'all-{example}-{stage}'
                    result = self.build(stage, name, extra)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    packet = self.base / name
                    self.assert_local_links_resolve(packet)
                    if stage == 'layout':
                        self.assertTrue((packet / 'family-selector.md').is_file())
                        self.assertFalse((packet / 'copy-style.json').exists())
                    else:
                        style = json.loads((packet / 'copy-style.json').read_text())
                        self.assertTrue(style['example'].startswith(f'example-{example:02d}'))
                        self.assertFalse((packet / 'style-reference.png').exists())
                        self.assertFalse((packet / 'family-selector.md').exists())

    def test_selection_has_two_layout_candidates_and_no_copy_material(self):
        result = self.build('select', 'selection', ['--candidates', '3', '15'])
        self.assertEqual(result.returncode, 0, result.stderr)
        packet = self.base / 'selection'
        inventory = json.loads((packet / 'candidate-layouts.json').read_text())
        self.assertEqual([r['example'] for r in inventory['candidates']], [3, 15])
        self.assert_local_links_resolve(packet)
        for row in inventory['candidates']:
            self.assertTrue((packet / row['image']).is_file())
        for excluded in ('copy-style.json', 'working-language.md', 'title.md', 'layout.json', 'brand-invariants.json'):
            self.assertFalse((packet / excluded).exists())
        rejected = self.build('select', 'duplicate-selection', ['--candidates', '3', '3'])
        self.assertNotEqual(rejected.returncode, 0)

    def test_focused_copy_carries_selected_grammar_without_full_source_archive(self):
        for number, family in ((15, 'evidence-led-short-readout'), (16, 'prose-led-overview-inset')):
            result = self.build('copy', f'new-copy-{number}', ['--layout', str(self.layout), '--example', str(number)])
            self.assertEqual(result.returncode, 0, result.stderr)
            packet = self.base / f'new-copy-{number}'
            style = json.loads((packet / 'copy-style.json').read_text())
            self.assertEqual(style['family'], family)
            self.assertTrue(style['bodyEvidence']['paragraphGrammar'])
            self.assertTrue(style['workingCadence'])
            self.assertNotIn('sourceVerbatim', style)
            self.assertFalse((packet / 'candidate-layouts.json').exists())

    def test_layout_preserves_same_case_selection_and_rejects_wrong_choice(self):
        choice = self.base / 'selection.json'
        decision = {'caseId': 'toy-routing', 'candidateExamples': [3, 15], 'selectedExample': 15,
                    'objectRole': 'principal evidence', 'reportIntent': 'Brief measured result readout',
                    'reason': 'The current evidence carries the detailed comparison.',
                    'alternativeRejection': 'The alternative reserves unnecessary explanatory prose.'}
        choice.write_text(json.dumps(decision))
        result = self.build('layout', 'selected-layout', ['--example', '15', '--selection', str(choice)])
        self.assertEqual(result.returncode, 0, result.stderr)
        carried = json.loads((self.base / 'selected-layout/selection.json').read_text())
        self.assertEqual(carried['selectedExample'], 15)
        wrong = self.build('layout', 'wrong-selected-layout', ['--example', '3', '--selection', str(choice)])
        self.assertNotEqual(wrong.returncode, 0)
        decision['caseId'] = 'another-case'
        choice.write_text(json.dumps(decision))
        foreign = self.build('layout', 'foreign-selected-layout', ['--example', '15', '--selection', str(choice)])
        self.assertNotEqual(foreign.returncode, 0)

    def test_focused_families_resolve_recorded_images_measurements_and_only_selected_modules(self):
        cases = [('runtime-focus-table', 12, 'runtime-focus-table', 'ablation'),
                 ('plot-led-runtime-observation', 13, 'plot-led-observation', 'ablation'),
                 ('compact-scientific-object-with-notes', 14, 'compact-object', 'mechanism')]
        focused = json.loads((ROOT / 'references/author-examples/focused-layout-starters.json').read_text())
        measured = json.loads((ROOT / 'references/author-examples/measurements-cfi.json').read_text())
        for family, number, module, specialist in cases:
            selected = next(f for f in focused['families'] if f['family'] == family)
            record = next(r for r in measured['records'] if r['example'] == selected['trainingExample'])
            for stage in ('layout', 'copy'):
                with self.subTest(family=family, stage=stage):
                    extra = ['--family', family, '--specialist', specialist]
                    if stage == 'copy':
                        extra.extend(['--layout', str(self.layout)])
                    name = f'focus-{number}-{stage}'
                    result = self.build(stage, name, extra)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    packet = self.base / name
                    self.assert_local_links_resolve(packet)
                    if stage == 'layout':
                        self.assertEqual((packet / 'style-reference.png').read_bytes(),
                            (ROOT / 'references/author-examples' / selected['trainingExample']).read_bytes())
                        self.assertEqual(json.loads((packet / 'layout-style.json').read_text()),
                            {k: v for k, v in selected.items() if k != 'titleGrammar'})
                        self.assertEqual((packet / 'focused-specialist.md').read_text().splitlines()[0],
                            (ROOT / f'references/layout/{module}.md').read_text().splitlines()[0])
                        self.assertNotIn('copy-style.json', [p.name for p in packet.iterdir()])
                    else:
                        style = json.loads((packet / 'copy-style.json').read_text())
                        self.assertEqual(style['titleEvidence']['actualText'],
                            [s['text'] for s in record['textSpans'] if 'Frank' in s['font']])
                        self.assertEqual(style['bodyEvidence']['voiceFragments'],
                            [s['text'] for s in record['textSpans'] if s['sizePt'] >= 12 and
                             'Arial' in s['font'] and len(s['text']) > 8])
                        self.assertEqual(style['roleGrammar'], selected['narrativeSlots'])
                        self.assertFalse((packet / 'family-selector.md').exists())
                        self.assertFalse((packet / 'focused-specialist.md').exists())
                        self.assertFalse((packet / 'brand-invariants.json').exists())

    def test_absent_title_remains_absent(self):
        result = self.build('copy', 'untitled-copy', ['--layout', str(self.layout), '--example', '8'])
        self.assertEqual(result.returncode, 0, result.stderr)
        style = json.loads((self.base / 'untitled-copy/copy-style.json').read_text())
        self.assertEqual(style['titleEvidence']['actualText'], [])
        self.assertFalse(style['titleEvidence']['present'])

    def test_selected_component_guides_arrive_without_unrelated_copy_context(self):
        table = self.build('layout', 'table-module', ['--example', '2'])
        self.assertEqual(table.returncode, 0, table.stderr)
        packet = self.base / 'table-module'
        self.assertEqual((packet / 'focused-specialist.md').read_text().splitlines()[0],
                         (ROOT / 'references/layout/scientific-table.md').read_text().splitlines()[0])
        self.assertFalse((packet / 'procedure-guide.md').exists())
        procedure = self.build('copy', 'procedure-module', ['--layout', str(self.layout), '--example', '22'])
        self.assertEqual(procedure.returncode, 0, procedure.stderr)
        self.assertTrue((self.base / 'procedure-module/procedure-guide.md').is_file())
        self.assert_local_links_resolve(self.base / 'procedure-module')
        readout = self.build('copy', 'readout-module', ['--layout', str(self.layout), '--example', '19'])
        self.assertEqual(readout.returncode, 0, readout.stderr)
        self.assertFalse((self.base / 'readout-module/procedure-guide.md').exists())

    def test_layout_original_selected_brand_and_regions(self):
        result = self.build('layout', 'layout', ['--example', '3'])
        self.assertEqual(result.returncode, 0, result.stderr)
        packet = self.base / 'layout'
        brand = json.loads((packet / 'brand-invariants.json').read_text())
        self.assertEqual(brand['selectedBrand'], 'nyu')
        asset = packet / brand['family']['asset']
        original = ROOT / 'assets/author-profile/nyu.png'
        self.assertEqual(asset.read_bytes(), original.read_bytes())
        self.assertIn('occupiedRegions', brand['family'])
        self.assertEqual(brand['pageMarker']['fontFamily'], 'Montserrat')
        self.assertFalse((packet / 'copy-style.json').exists())
        self.assertFalse((packet / 'brand-assets/sai-lab.png').exists())

    def test_reject_copy_given_downstream_draft(self):
        draft = self.base / 'draft.json'
        draft.write_text(json.dumps(toy_copy(self.facts)))
        result = self.build('copy', 'bad-copy', ['--layout', str(self.layout), '--example', '1', '--copy', str(draft)])
        self.assertNotEqual(result.returncode, 0)

    def test_declared_relative_asset_is_verified_and_rebased(self):
        source = self.base / 'toy-figure.txt'
        source.write_text('A generic toy scientific asset.')
        facts = toy()
        facts['assets'] = [{'id': 'figure', 'source': 'toy notes: attachment', 'path': source.name,
                            'sha256': hashlib.sha256(source.read_bytes()).hexdigest()}]
        facts_file = self.base / 'asset-facts.json'
        facts_file.write_text(json.dumps(facts))
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/make_stage_packet.py'), 'layout',
            '--facts', str(facts_file), '--specialist', 'mechanism', '--example', '1',
            '--out', str(self.base / 'asset-layout'), '--evidence', str(source)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        frozen = json.loads((self.base / 'asset-layout/facts.json').read_text())
        self.assertEqual(frozen['assets'][0]['path'], 'evidence/toy-figure.txt')
        self.assertEqual((self.base / 'asset-layout/evidence/toy-figure.txt').read_bytes(), source.read_bytes())
        source.write_text('Changed after facts were frozen.')
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/make_stage_packet.py'), 'layout',
            '--facts', str(facts_file), '--specialist', 'mechanism', '--example', '1',
            '--out', str(self.base / 'stale-asset-layout'), '--evidence', str(source)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('sha256', result.stderr)

    def test_reject_undeclared_evidence(self):
        extra = self.base / 'unlisted.txt'
        extra.write_text('unrelated scientific asset')
        result = self.build('layout', 'bad-evidence', ['--example', '1', '--evidence', str(extra)])
        self.assertNotEqual(result.returncode, 0)


    def test_saved_page_style_check_is_narrow_and_hashes_actual_files(self):
        from base64 import b64decode
        image = self.base / 'saved.png'
        image.write_bytes(b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIHWP4z8DwHwAFgAI/ScLbtAAAAABJRU5ErkJggg=='))
        intent = self.base / 'intent.json'
        intent.write_text(json.dumps({'argumentRole':'bounded comparison','audience':'internal collaborators',
                                     'oldReview':'EXCLUDE THIS'}))
        command = [sys.executable, str(ROOT / 'scripts/make_stage_packet.py'), 'style-check',
                   '--saved-page', str(image), '--intent', str(intent), '--example','19']
        result = subprocess.run(command + ['--out',str(self.base/'style-check')],text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)
        packet = self.base/'style-check'
        self.assertEqual({p.name for p in packet.iterdir()}, {'saved-page.png','style-reference.png',
            'style-measurements.json','intent.json','stage-guide.md','packet-manifest.json'})
        self.assertEqual(json.loads((packet/'intent.json').read_text()),
                         {'argumentRole':'bounded comparison','audience':'internal collaborators'})
        manifest=json.loads((packet/'packet-manifest.json').read_text())
        self.assertEqual(manifest['fileSha256']['saved-page.png'],hashlib.sha256(image.read_bytes()).hexdigest())
        result=subprocess.run(command+['--out',str(self.base/'bad-style-check'),'--facts',str(self.f)],text=True,capture_output=True)
        self.assertNotEqual(result.returncode,0)

    def test_facts_packet_excludes_nested_drafts_and_preserves_equations(self):
        facts,layout,copy = joint_toy()
        facts['facts'][0]['privateSourceDraft'] = 'EXCLUDE THIS RAW PARAGRAPH'
        facts['tables'][0]['draft'] = 'EXCLUDE'
        f=self.base/'joint-facts.json'; f.write_text(json.dumps(facts))
        result=subprocess.run([sys.executable,str(ROOT/'scripts/make_stage_packet.py'),'layout',
            '--facts',str(f),'--specialist','mechanism','--example','19','--out',str(self.base/'clean-facts')],text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)
        frozen=(self.base/'clean-facts/facts.json').read_text()
        self.assertNotIn('EXCLUDE',frozen)
        self.assertEqual(json.loads(frozen)['equations'],facts['equations'])

    def test_copy_plan_drops_attached_source_drafts(self):
        layout = json.loads(self.layout.read_text())
        layout['draftedBodySentences'] = ['EXCLUDE SOURCE DRAFT']
        layout['slots'] = [{'id':'heading','rawParagraphs':['EXCLUDE NESTED RAW']}]
        plan = self.base/'attached-layout.json'; plan.write_text(json.dumps(layout))
        result=self.build('copy','no-drafts',['--layout',str(plan),'--example','1'])
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertNotIn('EXCLUDE',(self.base/'no-drafts/layout.json').read_text())


if __name__ == '__main__':
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / 'toy-facts.json').write_text(json.dumps(toy(), indent=2))
    (WORK / 'toy-copy.json').write_text(json.dumps(toy_copy(toy()), indent=2))
    unittest.main(verbosity=2)
