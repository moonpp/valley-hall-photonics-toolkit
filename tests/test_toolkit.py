import copy
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from valleyhall import channel_status, reference_regime, replay
from valleyhall.replay import load_checked, TARGETS

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'examples/design_b'


def synthetic():
    return {'schema_version': 1, 'gap': [0.1, 0.9], 'samples': [
        {'s': i/8, 'modes': [
            {'eigen_index': j, 'f': 0.5, 'f_im': 0.01*(1+i%2),
             'te': 0.8, 'W_max': 0.8, 'wall': wall}
            for j, wall in enumerate(('SS','LL'))]} for i in range(8)]}


class ChannelTests(unittest.TestCase):
    def test_analytic_open_closed_grazing(self):
        self.assertEqual(channel_status(.2, .3, 2)['status'], 'open')
        self.assertEqual(channel_status(.2, .3, 1)['status'], 'closed')
        self.assertEqual(channel_status(.25, .5, 2)['status'], 'threshold')

    def test_time_reversal_symmetry(self):
        self.assertEqual(channel_status(.2, -.3, 2), channel_status(.2, .3, 2))

    def test_near_threshold_is_not_exact_claim(self):
        self.assertEqual(channel_status(.25 + 1e-14, .5, 2)['status'], 'threshold')
        self.assertEqual(channel_status(.25 + 1e-14, .5, 2, tolerance=0)['status'], 'open')

    def test_invalid_values(self):
        for value in (0, -1, float('nan'), float('inf'), True, '1'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                channel_status(value, .3, 1)
        for k in (.51, -.51, float('nan')):
            with self.assertRaises(ValueError):
                channel_status(.2, k, 1)
        with self.assertRaises(ValueError):
            channel_status(.2, .3, 1, tolerance=-1)

    def test_overflow_rejected(self):
        with self.assertRaises(ValueError):
            channel_status(1e308, .3, 1e308)

    def test_regimes(self):
        for rho, expected in ((3,'I'),(1.5,'II'),(1.2,'III'),(.8,'IV')):
            self.assertEqual(reference_regime((2/3)/rho, 1)['regime'], expected)

    def test_boundaries(self):
        for rho in (1,4/3,2):
            self.assertEqual(reference_regime((2/3)/rho, 1)['regime'], 'boundary')


class ReplayTests(unittest.TestCase):
    def test_archive(self):
        results = replay(load_checked(DATA))
        for wall in TARGETS:
            self.assertLess(abs(results[wall]['Q_rate_average']/TARGETS[wall]-1), 1e-12)
            self.assertEqual(results[wall]['retained_phases'],8)

    def test_rate_not_q_average(self):
        result = replay(synthetic())['SS']
        self.assertAlmostEqual(result['Q_rate_average'], .5/(2*.015))
        arithmetic = sum(m['Q_phase'] for m in result['selected_modes'])/8
        self.assertGreater(abs(arithmetic-result['Q_rate_average']), 2)

    def test_empty_samples_fail(self):
        data = synthetic(); data['samples'] = []
        with self.assertRaises(ValueError): replay(data)

    def test_duplicate_phase_fails(self):
        data = synthetic(); data['samples'][1]['s'] = 0
        with self.assertRaises(ValueError): replay(data)

    def test_missing_selection_fails(self):
        data = synthetic(); data['samples'][0]['modes'][0]['te'] = .59
        with self.assertRaises(ValueError): replay(data)

    def test_strict_gap_and_inclusive_weights(self):
        data = synthetic()
        for sample in data['samples']:
            for mode in sample['modes']: mode.update(te=.6,W_max=.6)
        replay(data)
        data['samples'][0]['modes'][0]['f'] = .1
        with self.assertRaises(ValueError): replay(data)

    def test_negative_zero_nan_decay_rejected(self):
        for value in (0, -.01, float('nan')):
            data = synthetic(); data['samples'][0]['modes'][0]['f_im'] = value
            with self.assertRaises(ValueError): replay(data)

    def test_tie_rejected(self):
        data = synthetic(); mode = copy.deepcopy(data['samples'][0]['modes'][0])
        mode['eigen_index'] = 2; data['samples'][0]['modes'].append(mode)
        with self.assertRaises(ValueError): replay(data)

    def test_highest_weight_selected(self):
        data = synthetic(); mode = copy.deepcopy(data['samples'][0]['modes'][0])
        mode.update(eigen_index=2, W_max=.9)
        data['samples'][0]['modes'].append(mode)
        self.assertEqual(replay(data)['SS']['selected_modes'][0]['eigen_index'],2)

    def test_permutation_invariance(self):
        data = synthetic(); expected = replay(data)
        data['samples'].reverse()
        for sample in data['samples']: sample['modes'].reverse()
        self.assertEqual(replay(data),expected)

    def test_duplicate_mode_fails(self):
        data = synthetic(); data['samples'][0]['modes'][1]['eigen_index'] = 0
        with self.assertRaises(ValueError): replay(data)

    def test_checksum_corruption_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            for path in DATA.glob('*.json'): shutil.copy(path,tmp)
            path = Path(tmp)/'modes.json'
            path.write_bytes(path.read_bytes()+b' ')
            with self.assertRaisesRegex(ValueError,'Checksum mismatch'): load_checked(tmp)

    def test_json_is_standard(self):
        def reject(value): raise ValueError(value)
        for path in DATA.glob('*.json'):
            json.loads(path.read_text(encoding='utf-8'), parse_constant=reject)

    def test_cli(self):
        run = subprocess.run([sys.executable,'-m','valleyhall','replay',str(DATA)],
                             cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(run.returncode,0,run.stderr)
        self.assertEqual(json.loads(run.stdout)['walls']['SS']['retained_phases'],8)

    def test_cli_invalid_input_fails(self):
        run = subprocess.run([sys.executable,'-m','valleyhall','screen','--frequency','nan',
                              '--upper-index','1','--lower-index','1.428'],
                             cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(run.returncode,2)


if __name__ == '__main__':
    unittest.main()
