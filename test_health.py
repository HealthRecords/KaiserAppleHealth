from pathlib import Path
from unittest import TestCase
from health import extract_value, list_vitals, list_prefixes


class Test(TestCase):
    def test_extract_values(self):
        test_file = "Observation-test-bp.json"
        observation = extract_value(test_file, "Blood Pressure")
        self.assertEqual(observation.name, "Blood Pressure" )
        self.assertEqual(observation.date, '2024-02-15T21:00:03Z')
        self.assertEqual(observation.data[0].value, 130)
        self.assertEqual(observation.data[0].unit, 'mm[Hg]')
        self.assertEqual(observation.data[0].name, 'Systolic blood pressure')
        self.assertEqual(observation.data[1].value, 88)
        self.assertEqual(observation.data[1].unit, 'mm[Hg]')
        self.assertEqual(observation.data[1].name, 'Diastolic blood pressure')

    def test_list_available(self):
        test_file = "Observation-test-bp.json"
        vitals = list_vitals([test_file])
        self.assertEqual(1, len(vitals))
        self.assertTrue("Blood Pressure" in vitals)

    def test_list_prefixes(self):
        vitals = list_prefixes(Path("."))
        self.assertEqual(1, len(vitals))
        self.assertEqual(2, vitals["Observation"])
