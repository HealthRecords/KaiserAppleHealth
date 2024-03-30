from unittest import TestCase

from xml_reader import find, trim
class Test(TestCase):
    def test_find(self):
        stack = [1,2,3]
        target = [2,3]
        self.assertTrue(find(stack, target))

        target = [3,2]
        self.assertFalse(find(stack, target))

        target = [3,2]
        stack = []
        self.assertFalse(find(stack, target))

    def test_trim(self):
        tag = "{urn:hl7-org:v3}text"
        self.assertEqual("text", trim(tag))

        tag = "text"
        self.assertEqual("text", trim(tag))

        tag = ""
        self.assertEqual("", trim(tag))

    def test_load(self):
        import xml.etree.ElementTree as ET

        for event, element in ET.iterparse("test_data/export_cda_fraction_source.xml", events=["start"]):
            if element.text:
                t = element.text.strip()
            else:
                t = element.text
            print(element, t)