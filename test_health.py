from pathlib import Path
from unittest import TestCase
from health import extract_value, list_vitals, list_prefixes, list_categories


class Test(TestCase):
    def test_extract_values(self):
        test_file = "test_data/Observation-test-bp.json"
        observation = extract_value(test_file, "Blood Pressure", category_name="Vital Signs")
        self.assertEqual(observation.name, "Blood Pressure" )
        self.assertEqual(observation.date, '2024-02-15T21:00:03Z')
        self.assertEqual(observation.data[0].value, 130)
        self.assertEqual(observation.data[0].unit, 'mm[Hg]')
        self.assertEqual(observation.data[0].name, 'Systolic blood pressure')
        self.assertEqual(observation.data[1].value, 88)
        self.assertEqual(observation.data[1].unit, 'mm[Hg]')
        self.assertEqual(observation.data[1].name, 'Diastolic blood pressure')

    def test_list_available(self):
        test_file = "test_data/Observation-test-bp.json"
        vitals = list_vitals([test_file], "Vital Signs")
        self.assertEqual(1, len(vitals))
        self.assertTrue("Blood Pressure" in vitals)

    def test_list_prefixes(self):
        vitals = list_prefixes(Path("test_data"))
        self.assertEqual(2, len(vitals))
        self.assertEqual(2, vitals["Observation"])
        self.assertEqual(1, vitals["MedicationRequest"])

    def test_categories(self):
        category_list, category_counter, count = list_categories(Path("test_data"), False, one_prefix=None)
        self.assertEqual(2, len(category_list))
        self.assertEqual(1, category_counter["Community"])
        self.assertEqual(2, category_counter["Vital Signs"])

        category_list, category_counter, count = list_categories(Path("test_data"), False, one_prefix='Observation')
        self.assertEqual(1, len(category_list))
        self.assertFalse("Community" in category_counter)
        self.assertEqual(2, category_counter["Vital Signs"])
