import json
import sys
from pathlib import Path
from typing import NoReturn
from unittest import TestCase
from health import extract_value, list_vitals, list_prefixes, list_categories, get_value_quantity, get_reference_range, \
    StatInfo, ValueQuantity, ReferenceRange


class Test(TestCase):
    def test_extract_values(self):
        test_file = "test_data/Observation-test-bp.json"
        observation = extract_value(test_file, StatInfo("Vital Signs", "Blood Pressure"))
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
        vitals = list_prefixes(Path("test_data/list_prefixes_test_dir"))
        self.assertEqual(2, len(vitals))
        self.assertEqual(2, vitals["Observation"])
        self.assertEqual(1, vitals["MedicationRequest"])

    def test_categories(self):
        category_list, category_counter, count = list_categories(Path("test_data/list_prefixes_test_dir"), False, one_prefix=None)
        self.assertEqual(2, len(category_list))
        self.assertEqual(1, category_counter["Community"])
        self.assertEqual(2, category_counter["Vital Signs"])

        category_list, category_counter, count = list_categories(Path("test_data"), False, one_prefix='Observation')
        self.assertEqual(1, len(category_list))
        self.assertFalse("Community" in category_counter)
        self.assertEqual(2, category_counter["Vital Signs"])

    def test_get_value_quantity(self):
        test_file = "test_data/ref_range.json"
        with open(test_file) as f:
            condition = json.load(f)
        v = condition["valueQuantity"]
        self.assertTrue(isinstance(v, dict))
        self.assertEqual(4, len(v))
        vq = get_value_quantity(v, "test")
        self.assertEqual('test', vq.name)

    def test_get_reference_range(self):
        # v_low = ValueQuantity(1.5, "g", "fake")
        # v_high = ValueQuantity(9.0, "g", "fake_high")
        # test = ReferenceRange(v_low, v_high, "some fake test")
        # self.assertEqual(1.5, test.low.value)
        # self.assertEqual(9.0, test.high.value)
        # self.assertEqual("some fake test", test.text)

        test_file = "test_data/ref_range.json"
        with open(test_file) as f:
            record = json.load(f)
        rr_info = record['referenceRange']
        self.assertIsNotNone(rr_info)
        self.assertTrue(isinstance(rr_info, list))
        self.assertEqual(1, len(rr_info))
        rr = get_reference_range(rr_info)

        self.assertEqual(140, rr.low.value)
        self.assertEqual("K/uL", rr.low.unit)
        self.assertEqual("low", rr.low.name)

        self.assertEqual(400, rr.high.value)
        self.assertEqual("K/uL", rr.high.unit)
        self.assertEqual("high", rr.high.name)

        l, h = rr.get_range()
        self.assertEqual(140, l)
        self.assertEqual(400, h)
        self.assertEqual("high", rr.high.name)

        self.assertEqual("140 - 400 K/uL", rr.text)

    def check_range(self, text:str, expect_low, expect_high) -> None:
        test = ReferenceRange(None, None, text )
        self.assertIsNone(test.low)
        self.assertIsNone(test.high)
        range_ = test.get_range()
        self.assertIsNotNone(range_)
        low, high = range_
        self.assertEqual(expect_low, low)
        self.assertEqual(expect_high, high)

    def test_get_reference_range_text(self):
        self.check_range("<7.5", -sys.maxsize, 7.5)
        self.check_range("<=7.6", -sys.maxsize, 7.6)

        self.check_range(">7.7", 7.7, sys.maxsize)
        self.check_range(">=7.8", 7.8, sys.maxsize)

        self.check_range("=7.9", 7.9, 7.9)

        test_file = "test_data/ref_range_text.json"
        with open(test_file) as f:
            record = json.load(f)
        rr_info = record['referenceRange']
        self.assertIsNotNone(rr_info)
        self.assertTrue(isinstance(rr_info, list))
        self.assertEqual(1, len(rr_info))
        rr = get_reference_range(rr_info)
        range_ = rr.get_range()
        print(rr, range_)



