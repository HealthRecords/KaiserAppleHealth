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
from collections import Counter


# TODO Finish interactive/menu user interface. Observations is just getting started.
# For interactive mode, I need to be consistent about print, plot, and active/inactive.
# TODO like medicines, conditions should have an option to print inactive.
# TODO print_condition and print_medicines should be generalized and combined.
# TODO Do we want to have an option to process multiple or all stats in one run?


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

def extract_value(file: str, sign_name: str, *, category_name) -> Observation | None:
    with open(file) as f:
        condition = json.load(f)
        category_info = condition['category']
        assert isinstance(category_info, list)
        for ci in category_info:
            if ci['text'] == category_name:
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

def yield_observation_files(dir_path: Path) -> Iterable[str]:
    for p in dir_path.glob("Observation*.json"):
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

def extract_all_values(observation_files: Iterable[str], sign_name: str, *, category_name) -> list[Observation]:
    """

    :param observation_files: iterable of files to read
    :param sign_name:  The name of the vital sign we want data for. (now, this is a code, within any category,
                       not just "Vital Signs")
    :category_name: Like "Vital Signs". It appears that all "Observation*.json" file have a category.
    :return: Instance of class Observation or None
    """
    values = []
    for p in observation_files:
        value = extract_value(p, sign_name, category_name=category_name)
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

def print_procedures(cd: Path, csv_format: bool, match: str) -> NoReturn:
    path = cd / match
    conditions = []
    for p in glob.glob(str(path)):
        with open(p) as f:
            condition = json.load(f)
            conditions.append(
                (condition['resourceType'],
                 condition['performedDateTime'],
                 condition['status'],
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

def print_medicines(cd: Path, csv_format: bool, match: str, include_inactive: bool) -> NoReturn:
    path = cd / match
    conditions = []
    for p in glob.glob(str(path)):
        with open(p) as f:
            condition = json.load(f)
            is_active = not condition['status'] in ['completed', 'stopped']
            if is_active or include_inactive:
                d = condition['authoredOn']
                # Line up printed columns
                if len(d) == 10:
                    d += 10*' '
                conditions.append(
                    (condition['resourceType'],
                     d,
                     condition['status'],
                     condition['medicationReference']['display'],
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


def list_vitals(observation_files: Iterable[str], category: str) -> Counter:
    vitals = Counter()
    signs_found = filter_category(observation_files, category)
    for observation in signs_found:
        code_name = observation['code']['text']
        vitals[code_name] += 1
    return vitals

def print_vitals(observation_files: Iterable[str], category: str) -> NoReturn:
    vitals = list_vitals(observation_files, category)
    print(F"Files that have a category of '{category}' were found in files. These codes were found in them.")
    v_sorted = sorted(vitals, key=lambda x: vitals[x], reverse=True)
    for v in v_sorted:
        print(F"{vitals[v]:6} {v}")

def list_prefixes(dir_path: Path) -> Counter:
    extensions = Counter()
    for p in dir_path.glob("*.json"):
        name = p.stem
        parts = name.split("-")
        prefix = parts[0]
        extensions[prefix] += 1
    return extensions


def print_prefixes(dir_path: Path) -> NoReturn:
    extensions = list_prefixes(dir_path)
    print(F"File prefixes found in {dir_path}")
    for ext, count in extensions.items():
        print(F"{count:6} {ext}")

def list_categories(dir_path: Path, only_first, *, one_prefix) -> (list[tuple], Counter, int):
    """
    The schema of this data is not well-designed. I have seen category expressed FOUR ways so far.

    "category":
        "CAT_NAME"

    "category": [
        "CAT_NAME",
        "CAT_NAME2"
    ]

    # Procedure-9EBC73F9-2883-416C-8C39-259B394A953D.json
    "category" : {
         "text" : "CAT_NAME",
    }

    # Observation-6A188217-E5D4-4A52-A762-7194900720FB.json
    category: [
        {
            "text":"CAT_NAME"
        }
    ]

    :param one_prefix: There are different kinds of documents, that start with "Observation" or "MedicationRequest"
    :                  For example, set this to "Observation" to only see categories from Observation files,
                       or set to None for all files.
    :param dir_path: Path of the directory to scan.
    :param only_first:  Only take the first category in a file. This is so we can see if there are any files without
                        categories.
    :return: c_sorted, counter, count
    """
    counter = Counter()
    count = 0
    wildcard = "*.json"
    if one_prefix:
        wildcard = one_prefix + wildcard

    for p in dir_path.glob(wildcard):
        with open(p) as f:
            count += 1
            observation_data = json.load(f)
            cat_top = observation_data["category"]
            if isinstance(cat_top, str):
                counter[cat_top] += 0.1
            elif isinstance(cat_top, dict):
                assert 'text' in ci
                assert isinstance(cat_top['text'], str)
                counter[cat_top['text']] += 1
            elif isinstance(cat_top, list):
                for ci in cat_top:
                    if isinstance(ci, str):
                        counter[ci] += 1
                    elif isinstance(ci, dict):
                        assert 'text' in ci
                        counter[ci['text']] += 1
                    if only_first:
                        break
            else:
                raise ValueError(F"File {p} has no category", p)

    c_sorted = sorted(counter, key=lambda x: counter[x], reverse=True)
    return c_sorted, counter, count

def print_categories(dir_path: Path, only_first, *, one_prefix) -> NoReturn:
    """

    :param dir_path:
    :param only_first:
    :param one_prefix:
    :return:
    """
    c_sorted, counter, count = list_categories(dir_path, only_first, one_prefix=one_prefix)
    print(F"Categories found in {count} files in {dir_path}")

    c2 = 0
    for index, key in enumerate(c_sorted):
        print(F"{index:3}: {key:.<32}: {counter[key]:>6}")
        c2 += counter[key]
    print(F"                                       {"======":>6}")
    print(F"{"":3}  Total categories found..........: {c2:>6}")
    print("Some files have more than one category. In particular, many files have both 'Lab' and 'Laboratory'")

    return counter


def parse_args():
    parser = argparse.ArgumentParser(description='Explore Kaiser Health Data',
                                     epilog='Example usage: python health.py -s Weight, --plot, --print')

    parser.add_argument('-a', '--allergy', action=argparse.BooleanOptionalAction,
                        help='Print all active allergies.')
    parser.add_argument('--after', type=str,
                        help='YYYY-MM-DD format date. Only include dates after this date when using --stat.')
    parser.add_argument('-c', '--conditions', action=argparse.BooleanOptionalAction,
                        help='Print all active conditions.')
    parser.add_argument('--categories', action=argparse.BooleanOptionalAction,
                        help='Print all active categories.')
    parser.add_argument('--csv-format', action=argparse.BooleanOptionalAction,
                        help='Format printed output as csv')
    parser.add_argument('-d', '--document-types', action=argparse.BooleanOptionalAction,
                        help='Show the types of documents in the clinical-records directory')
    parser.add_argument('-g', '--generic', type=str,
                        help='Lets you specify a category and a code, like -g Vital-signs:Weight. See --categories')
    parser.add_argument('-i', '--interactive', action=argparse.BooleanOptionalAction,
                        help='In interactive mode,  you will be prompted for choices.')
    parser.add_argument('-l', '--list-vitals', action=argparse.BooleanOptionalAction,
                        help='List names of all vital signs that were found.')
    parser.add_argument('-m', '--medicines', action=argparse.BooleanOptionalAction,
                        help='List all active medicines that were found.')
    parser.add_argument('--medicines-all', action=argparse.BooleanOptionalAction,
                        help='List all active medicines that were found.')
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
    active = [args.allergy, args.condition, args.document_types, args.list_vitals, args.medicines, args.medicines_all,
              args.categories, args.stat, args.generic, args.interactive]
    flags = ["-a", "-c", "-d", "-l", "-m", "--medicines-all", "--categories", "-s", "-g", "-i"]
    return args, active, flags

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

def do_vital(condition_path: Path, vital: str, after: str, print_data: bool, vplot: bool, csv_format: bool,
             *, category_name) -> NoReturn:
    if not print_data and not vplot:
        print("You need to select at least one of --plot or --print with --stat")
        return

    ws = extract_all_values(yield_observation_files(condition_path), vital, category_name=category_name)

    if after:
        ad = datetime.strptime(after, '%Y-%m-%d')
        ws = [w for w in ws if ad < datetime.strptime(w.date, '%Y-%m-%dT%H:%M:%SZ')]

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


def menu(choices: list[str]):
    option = -1
    while option < 1 or option > len(choices):
        for index, choice in enumerate(choices):
            print(f"[{index+1:3}] {choice}")
        print(f"[{"q":>3}] {"quit"}")
        print("Choose an option: ", end="")
        c = input()
        if c.strip() == "q":
            return -1, "quit"
        option = int(c)
    return option - 1, choices[option - 1]

def user_interface_observation(data_dir: Path, args):
    """
    Observations are anything measured. Test results, measurements of height or weight, etc.

    :param data_dir:
    :param args:
    :return:
    """
    list_cat, dict_cat, file_count = list_categories(data_dir, False, one_prefix=None)
    while (option := menu(list_cat))[0] != -1:
        option_number, category = option
        vitals = list_vitals(yield_observation_files(data_dir), category)
        vital_list = [k for k in vitals.keys()]
        while (choices := menu(vital_list))[0] != -1:
            choice_number, choice_string = choices
            do_vital(data_dir, choice_string, args.after, True, True, args.csv_format,
                     category_name=category)
        print("You want information about ", option[1])
        # print("Would you like to print or plot this?")
    return

def user_interface(condition_path: Path, args) -> None:
    """
    display menus on the command line

    :param args:
    :param condition_path:
    :return: No Return
    """
    print()
    options = list(list_prefixes(condition_path).keys())
    while (var := menu(options))[0] != len(options):
        value = var[1]
        match value:
            case "quit":
                return
            case "Observation":
                user_interface_observation(condition_path, args)
            case "MedicationRequest":
                include_inactive, v = menu(["Active Medicines", "All Medicines"])
                include_inactive = bool(include_inactive)
                print_medicines(condition_path, args.csv_format, "MedicationRequest*.json", include_inactive)
            case "DocumentReference":
                print("I don't know anything about DocumentReferences, yet.")
            case "Condition":
                print_conditions(condition_path, args.csv_format, "Condition*.json")
            case "AllergyIntolerance":
                print_conditions(condition_path, args.csv_format, "AllergyIntolerance*.json")
            case "Procedure":
                print_procedures(condition_path, args.csv_format, "Procedure*.json")
            case _:
                print("I don't know anything about " + value + " files, yet.")
    return


def go():
    args, active, flags = parse_args()
    base = Path("export/apple_health_export")
    condition_path = base / "clinical-records"

    if not any(active):
        print(F"Please select one of {flags} to get some output.")
        return

    if args.interactive:
        user_interface(condition_path, args)
        return

    if args.condition:
        print_conditions(condition_path, args.csv_format, "Condition*.json")

    if args.allergy:
        print_conditions(condition_path, args.csv_format, "All*.json")

    if args.medicines or args.medicines_all:
        include_inactive = False
        if args.medicines_all:
            include_inactive = True
        print_medicines(condition_path, args.csv_format, "MedicationRequest*.json", include_inactive)

    if args.stat:
        do_vital(condition_path, args.stat, args.after, args.print, args.plot, args.csv_format, category_name="Vital Signs")

    if args.list_vitals:
        print_vitals(observation_files=yield_observation_files(condition_path), category="Vital Signs")

    if args.generic:
        param = args.generic.split("#", 1)
        assert isinstance(param, list)
        if len(param) == 1:
            print_vitals(observation_files=yield_observation_files(condition_path), category=param[0])
        elif len(param) == 2:
            do_vital(condition_path, param[1], args.after, args.print, args.plot, args.csv_format,
                     category_name=param[0])
        else:
            print("Invalid format: use -g category:code     like '-g \"Vital Signs:Blood Pressure\"")

    if args.categories:
        print_categories(condition_path, only_first=False, one_prefix=None)

    if args.document_types:
        print_prefixes(condition_path)

if __name__ == "__main__":
    go()
