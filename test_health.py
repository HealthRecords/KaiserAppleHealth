from pathlib import Path
from unittest import TestCase
from health import extract_value


class Test(TestCase):
    def test_extract_values(self):
        test_file = "Observation-test-bp.json"
        observation = extract_value(test_file, "Blood Pressure")
        self.assertEqual(observation[0], "Blood Pressure" )
        self.assertEqual(observation[1], '2024-02-15T21:00:03Z')
        self.assertEqual(observation[2][0].value, 130)
        self.assertEqual(observation[2][0].unit, 'mm[Hg]')
        self.assertEqual(observation[2][0].name, 'Systolic blood pressure')
        self.assertEqual(observation[2][1].value, 88)
        self.assertEqual(observation[2][1].unit, 'mm[Hg]')
        self.assertEqual(observation[2][1].name, 'Diastolic blood pressure')

