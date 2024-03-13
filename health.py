import glob
import json
from io import StringIO
from pathlib import Path
from typing import NoReturn, Iterable
import argparse
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import csv
from dataclasses import dataclass

# TODO There are more types of json documents that I had seen. Add a method to print all types, then go from there.
# TODO Do we want to have an option to process multiple or all stats in one run?
# TODO Option to list all types of documents found.

@dataclass
class ValueQuantity:
    """
    Represents a "valueQuantity", from an Observation. It provides a value, a unit and optionally a name.

    We are combining two objects from the documentation.

    For Observations with a single value, the Observation contains one valueQuantity object.
    For Observations with multiple values, there is a "component", which contains a valueObject and "code" with a name
     for each individual value.
    a name field (single valued fields use the category text).

    We ignore system, and the duplicate name.

    "valueQuantity" : {
        "code" : "mg/dL",
        "value" : 0.90,
        "system" : "http://unitsofmeasure.org",
        "unit" : "mg/dL"
  },
    """
    value: float
    unit: str
    name: str

@dataclass
class Observation:
    """
    This holds data from one file, which records an observation, such as height or blood pressure.
    """
    name: str
    date: str
    data: list[ValueQuantity]


def convert_units(v, u):
    # TODO this should be optional, but we are parsing US data.
    if u == "kg":
        v = v * 2.2
        u = "lb"
    elif u == "Cel":
        v = v * 9.0 / 5.0 + 32.0
        u = "Fah"
    return v, u

def extract_value(file: str, sign_name: str) -> Observation | None:
    with open(file) as f:
        condition = json.load(f)
        category_info = condition['category']
        assert isinstance(category_info, list)
        for ci in category_info:
            if ci['text'] == "Vital Signs":
                if condition['code']['text'] == sign_name:
                    t = sign_name
                    d = condition['effectiveDateTime']
                    # It turns out that blood pressure, which has two values, like 144/100,
                    # has a slightly different format. First find "component", then each has
                    # its own "valueQuantity"
                    if "valueQuantity" in condition:
                        v = condition["valueQuantity"]["value"]
                        u = condition["valueQuantity"]["unit"]
                        v, u = convert_units(v, u)
                        vq = ValueQuantity(v, u, sign_name)
                        return Observation(t, d, [vq])

                    elif "component" in condition:
                        sub_values = []
                        for component in condition["component"]:
                            val = component["valueQuantity"]["value"]
                            unit = component["valueQuantity"]["unit"]
                            text = component["code"]["text"]
                            val, unit = convert_units(val, unit)
                            vq = ValueQuantity(val, unit, text)

                            sub_values.append(vq)
                        return Observation(t, d, sub_values)
    return None

def yield_observations(cd: Path) -> Iterable[str]:
    path = cd / "Observation*.json"
    for p in glob.glob(str(path)):
        yield p

def filter_category(observation_files: Iterable[str], category: str) -> Iterable[dict]:
    """
    Filters observations, only passing on those with a category['text'] = category
    :param observation_files: Source for file names
    :param category: The name of the category to keep, like 'Vital Signs'
    :return:
    """
    for file in observation_files:
        with open(file) as f:
            observation = json.load(f)
            category_info = observation['category']
            assert isinstance(category_info, list)
            for ci in category_info:
                if ci['text'] == category:
                    yield observation

def extract_all_values(observations: Iterable[str], sign_name: str) -> list[Observation]:
    values = []
    for p in observations:
        value = extract_value(p, sign_name)
        if value is not None:
            values.append(value)
    values = sorted(values, key=lambda x: x.date)
    return values

def print_csv(data: Iterable):
    output = StringIO()
    wr = csv.writer(output, quoting=csv.QUOTE_ALL)
    wr.writerow(data)
    print(output.getvalue(), end="")


def print_conditions(cd: Path, csv_format: bool, match: str) -> NoReturn:
    path = cd / match
    conditions = []
    for p in glob.glob(str(path)):
        with open(p) as f:
            condition = json.load(f)
            conditions.append(
                (condition['resourceType'],
                 condition['recordedDate'],
                 condition['clinicalStatus']['coding'][0]['code'],
                 condition['verificationStatus']['coding'][0]['code'],
                 condition['code']['text'],
                 )
            )
    cs = sorted(conditions, key=lambda x: x[1])
    for condition in cs:
        if csv_format:
            print_csv(condition)
        else:
            # Almost the same as csv, but the csv version escapes special characters, if there are any.
            print(condition)

def print_value(w: Observation):
    print(F"{w.name:10}: {w.date} - ", end="")
    values = w.data
    for value in values:
        print(F" {value.value:6.1f} {value.unit},", end="")
    print()

def print_value_csv(w: Observation):
    fields = [w.name, w.date]
    values = w.data
    for value in values:
        fields.append(value.value)
        fields.append(value.unit)
        fields.append(value.name)
    print_csv(fields)

def print_values(ws: list[Observation], csv_format: bool) -> NoReturn:
    for w in ws:
        if csv_format:
            print_value_csv(w)
        else:
            print_value(w)


def list_vitals(observation_files: Iterable[str]) -> set[str]:
    vitals = set()
    signs_found = filter_category(observation_files, "Vital Signs")
    for observation in signs_found:
        code_name = observation['code']['text']
        vitals.add(code_name)
    return vitals

def print_vitals(observation_files: Iterable[str]) -> NoReturn:
    vitals = list_vitals(observation_files)
    print("Vital Statistics found in records.")
    for stat in sorted(vitals):
        print("\t", stat)

# def list_record_types(observation_files: Iterable[str]) -> set[str]:
#     vitals = set()
#     signs_found = filter_category(observation_files, "Vital Signs")
#     for observation in signs_found:
#         code_name = observation['code']['text']
#         vitals.add(code_name)
#     return vitals
#
# def print_record_types(observation_files: Iterable[str]) -> NoReturn:
#     vitals = list_vitals(observation_files)
#     print("Vital Statistics found in records.")
#     for stat in sorted(vitals):
#         print("\t", stat)

def parse_args():
    parser = argparse.ArgumentParser(description='Explore Kaiser Health Data',
                                     epilog='Example usage: python health.py -s Weight, --plot, --print')

    parser.add_argument('-a', '--allergy', action=argparse.BooleanOptionalAction,
                        help='Print all active allergies.')
    parser.add_argument('--after', type=str,
                        help='YYYY-MM-DD format date. Only include dates after this date when using --stat.')
    parser.add_argument('-c', '--condition', action=argparse.BooleanOptionalAction,
                        help='Print all active conditions.')
    parser.add_argument('--csv-format', action=argparse.BooleanOptionalAction,
                        help='Format printed output as csv')
    # parser.add_argument('--d', '--document-types', action=argparse.BooleanOptionalAction,
    #                     help='Show the types of documents in the clinical-records directory')
    parser.add_argument('-l', '--list-vitals', action=argparse.BooleanOptionalAction,
                        help='List names of all vital signs that were found.')
    parser.add_argument('--plot',  action=argparse.BooleanOptionalAction,
                        help='Plots the vital statistic selected with --stat.')
    parser.add_argument('--print', action=argparse.BooleanOptionalAction,
                        help='Prints the vital statistic selected with --stat.')
    parser.add_argument('-s', '--stat', type=str,
        help='Print a vital statistic, like weight. Name has to match EXACTLY, ' +
            'Weight" is not "weight".\nSome examples:\n' +
            'SpO2, Weight, "Blood Pressure" (quotes are required, if the name has spaces in it).' +
            'use the -l to get a list of stats found in your data.')
    args = parser.parse_args()
    return args

def plot(dates, values: list[float], values2: list[float], graph_subject, data_name_1, data_name_2) -> None:
    label0 = data_name_1 if data_name_1 else ""
    label1 = data_name_2 if data_name_2 else ""

    dates = [datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ') for date in dates]

    # Find the date range
    min_date = min(dates)
    max_date = max(dates)
    num_intervals = 6

    date_range = max_date - min_date
    interval_length = date_range / num_intervals

    # Determine and set the locator and formatter directly
    if interval_length < timedelta(days=70):  # Less than ~10 weeks
        locator = mdates.WeekdayLocator(interval=max(1, int(interval_length.days / 7)))
        date_format = mdates.DateFormatter('%Y-%m-%d')
    elif interval_length < timedelta(days=365):
        locator = mdates.MonthLocator()
        date_format = mdates.DateFormatter('%Y-%m')
    else:
        locator = mdates.YearLocator()
        date_format = mdates.DateFormatter('%Y')

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(dates, values, marker='o', label=label0)
    if values2 is not None:
        plt.plot(dates, values2, marker='x', linestyle='--', label=label1)

    plt.legend()
    # Set the locator and formatter
    plt.gca().xaxis.set_major_locator(locator)
    plt.gca().xaxis.set_major_formatter(date_format)

    plt.gcf().autofmt_xdate()  # Rotate dates for better spacing

    plt.title(F'Plot of {graph_subject} vs Date')
    plt.xlabel('Date')
    plt.ylabel(graph_subject)
    plt.grid(True)
    plt.tight_layout()

    plt.show()

def do_vital(condition_path: Path, vital: str, after: str, print_data: bool, vplot: bool, csv_format: bool) -> NoReturn:
    ws = extract_all_values(yield_observations(condition_path), vital)
    if after:
        ad = datetime.strptime(after, '%Y-%m-%d')
        ws = [w for w in ws if ad < datetime.strptime(w.date, '%Y-%m-%dT%H:%M:%SZ')]
    if not print_data and not vplot:
        print("You need to select at least one of --plot or --print with --stat")
        return
    if not ws:
        print(F"No data was found for stat {vital} ")
        if after:
            print(F"In the range of values after {after}")
        print(F"You can use the -l argument to see what stats are in your data.")
        return

    if print_data:
        print_values(ws, csv_format)

    if vplot:
        dates = [observation.date for observation in ws]
        # Assume lists are homogenous (all have same number and type of fields)
        first = ws[0]
        # Assume all valueQuantities are either list, or not list.
        if len(first.data) == 2:
            # The only multivalued field I have seen so far is blood pressure, with two values.
            values_1 = [observation.data[0].value for observation in ws]
            values_2 = [observation.data[1].value for observation in ws]
            data_name_1 = first.data[0].name
            data_name_2 = first.data[1].name
        elif len(first.data) == 1:
            values_1 = [observation.data[0].value for observation in ws]
            values_2 = None
            data_name_1 = vital
            data_name_2 = None
        else:
            raise ValueError(f"Unexpected number of data values. {len(first.data)}.")

        plot(dates, values_1, values_2, vital, data_name_1, data_name_2)


def go():
    # vital, condition, lv, vplot, print_data, after, csv_format, allergy = parse_args()
    args = parse_args()
    base = Path("export/apple_health_export")
    condition_path = base / "clinical-records"

    if not args.condition and not args.stat:
        print("Please select either -s, -c or -l to get some output.")
        return

    if args.condition:
        print_conditions(condition_path, args.csv_format, "Condition*.json")

    if args.allergy:
        print_conditions(condition_path, args.csv_format, "All*.json")

    if args.stat:
        do_vital(condition_path, args.stat, args.after, args.print, args.plot, args.csv_format)

    if args.list_vitals:
        print_vitals(observation_files=yield_observations(condition_path))

if __name__ == "__main__":
    go()
