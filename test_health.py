from pathlib import Path
from unittest import TestCase
from health import extract_value


class Test(TestCase):
    def test_extract_values(self):
        test_file = "Observation-test-bp.json"
        w = extract_value(test_file, "Blood Pressure")
        self.assertEqual(w[0], "Blood Pressure" )
        self.assertEqual(w[1], '2024-02-15T21:00:03Z')
        self.assertEqual(w[2][0][0], 130)
        self.assertEqual(w[2][0][1], 'mm[Hg]')
        self.assertEqual(w[2][0][2], 'Systolic blood pressure')
        self.assertEqual(w[2][1][0], 88)
        self.assertEqual(w[2][1][1], 'mm[Hg]')
        self.assertEqual(w[2][1][2], 'Diastolic blood pressure')

