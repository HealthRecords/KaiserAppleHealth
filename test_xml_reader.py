from unittest import TestCase

from xml_reader import find, trim, find_display_names, gen


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
            # print(element, t)

    def test_find_display_names(self):
        display_names, element_stack = find_display_names(
            "test_data/test_find_display_names.xml", ["organizer", "code"])
        self.assertEqual(1, len(display_names))
        self.assertEqual(0, len(element_stack))
        display_names, element_stack = find_display_names(
            "test_data/test_find_display_names.xml", ["component", "observation", "code"])
        self.assertEqual(2, len(display_names))
        self.assertEqual(0, len(element_stack))



