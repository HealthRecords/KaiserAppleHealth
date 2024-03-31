"""
Some apple health data comes in xml files.There are two, export.xml, and export_cda.xml. I haven't fully
determined what is in these files. I can see data that is sourced from an apple watch, and that is sourced
from third party devices that write to apple health.

All top level tags from export.xml:
    {'WorkoutEvent', 'Record', 'MetadataEntry', 'InstantaneousBeatsPerMinute', 'ActivitySummary',
    'HeartRateVariabilityMetadataList', 'ClinicalRecord', 'ExportDate', 'Workout', 'HealthData',
    'WorkoutStatistics', 'FileReference', 'WorkoutRoute', 'Me'}

All tags from export_cda.xml:

{'{urn:hl7-org:v3}high', '{urn:hl7-org:v3}sourceName', '{urn:hl7-org:v3}unit', '{urn:hl7-org:v3}component',
'{urn:hl7-org:v3}patient', '{urn:hl7-org:v3}effectiveTime', '{urn:hl7-org:v3}type', '{urn:hl7-org:v3}templateId',
'{urn:hl7-org:v3}realmCode', '{urn:hl7-org:v3}administrativeGenderCode', '{urn:hl7-org:v3}statusCode',
'{urn:hl7-org:v3}key', '{urn:hl7-org:v3}organizer', '{urn:hl7-org:v3}ClinicalDocument', '{urn:hl7-org:v3}text',
'{urn:hl7-org:v3}value', '{urn:hl7-org:v3}low', '{urn:hl7-org:v3}entry', '{urn:hl7-org:v3}id', '{urn:hl7-org:v3}typeId',
'{urn:hl7-org:v3}sourceVersion', '{urn:hl7-org:v3}recordTarget', '{urn:hl7-org:v3}observation',
'{urn:hl7-org:v3}confidentialityCode', '{urn:hl7-org:v3}title', '{urn:hl7-org:v3}device', '{urn:hl7-org:v3}patientRole',
'{urn:hl7-org:v3}interpretationCode', '{urn:hl7-org:v3}name', '{urn:hl7-org:v3}metadataEntry', '{urn:hl7-org:v3}code',
'{urn:hl7-org:v3}birthTime'}


Using https://realpython.com/python-xml-parser/#xmletreeelementtree-a-lightweight-pythonic-alternative

"""
import argparse
import sys
import unicodedata
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from collections import Counter
from math import log10


@dataclass
class Observation:
    name: str
    value: str
    unit: str
    sourceName: str

    def __init__(self, name: str):
        self.name = name


def find(stack: list[str], target: list[str]) -> bool:

    if len(target) > len(stack):
        return False
    for x in range(1, len(target)+1):
        if target[-x] != stack[-x]:
            return False
    return True

def trim(tag:str) -> str:
    """
    All the tags are namespaced in the same namespace, so it doesn't matter. Trim it off for simplicity.
    :param tag:
    :return:
    """
    if "}" not in tag:
        return tag
    return tag[tag.find("}")+1:]

def clean_tag(tag:str) -> str:
    tag = unicodedata.normalize("NFKD", trim(tag))
    return tag

def gen(file_name: str, events):
    for index, i in enumerate(ET.iterparse(file_name, events=events)):
        event, element = i
        yield index, event, element

def find_display_names(file_name: str, pattern: list[str]):
    element_stack = []
    display_names = Counter()
    for index, event, element in gen(file_name, ["start", "end"]):
        tag = clean_tag(element.tag)
        if event == "start":
            element_stack.append(tag)
            if find(element_stack, target=pattern):
                display_names[element.attrib['displayName']] += 1
        elif event == "end":
            element_stack.pop()
    return display_names, element_stack  # Only returning element_stack for test.


def go():
    tags = set()
    element_stack = []
    # file_name = "test_data/export_cda_fraction.xml"
    file_name = "export/apple_health_export/export_cda.xml"
    # file_name = "test_data/export_cda_1000.xml"
    count = 0
    count_sources = 0
    none_count = 0
    for index, i in enumerate(ET.iterparse(file_name, events=("start", "end"))):
        event, element = i
        tag = unicodedata.normalize("NFKD", trim(element.tag))
        tags.add(tag)
        if event == "start":
            # print(tag, element.attrib, element_stack)
            element_stack.append(tag)
            # print(element, element.attrib, element.text)
            if find(element_stack, ["component", "observation", "code"]):
                ob = Observation(element.attrib['displayName'])
            elif find(element_stack, ["text", "value"]):
                ob.value = element.text
            elif tag == "unit":
                ob.unit = element.text
                count += 1
                print(F"{index:7}: {count_sources}: {ob}")
        elif event == "end":
            if find(element_stack, ["text", "sourceName"]):
                count_sources += 1
                if element.text is None:
                    # print("None")
                    none_count += 1
                    ob.sourceName = "None"
                else:
                    ob.sourceName = unicodedata.normalize("NFKD", element.text)
            element_stack.pop()
    print(F"Found {count} observations.")
    print(F"None count {none_count}")
    print_tags: bool = False
    if print_tags:
        print("All Tags:")
        for tag in sorted(tags):
            print(tag)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Investigate data from Apple Health export.\nNote that "
                                     "an export can be millions of records, so this can take a long time.")
    parser.add_argument("-l", "--list", action="store_true", help="List all observations. SLOW! (minutes)")
    args = parser.parse_args()
    if args.list:
        print("This may take a few minutes...")
        names, _ = find_display_names("export/apple_health_export/export_cda.xml", ["component", "observation", "code"])
        max_count_name = max(names, key=names.get)
        max_count = names[max_count_name]

        lmc = log10(max_count) + 1
        print(max_count, lmc)
        for index, _ in enumerate(names.most_common()):
            name, count = _
            print(F"{index:6}: [{count:10,}] {name} ")
        sys.exit(1)
    else:
        go()