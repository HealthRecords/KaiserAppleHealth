import glob
import json
from pathlib import Path
from typing import NoReturn
import argparse

# TODO Print mix and max values?

def extract_value(file: str, sign_name: str) -> tuple|None:
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
                        w = condition["valueQuantity"]["value"]
                        u = condition["valueQuantity"]["unit"]
                        return t, d, (w, u)

                    elif "component" in condition:
                        sub_values = []
                        for component in condition["component"]:
                            val = component["valueQuantity"]["value"]
                            unit = component["valueQuantity"]["unit"]
                            sub_values.append((val, unit))
                        return t, d, sub_values
    return None

def extract_all_values(cd: Path, sign_name: str) -> list[tuple]:
    path = cd / "Observation*.json"
    values = []
    for p in glob.glob(str(path)):
        value = extract_value(p, sign_name)
        if value is not None:
            values.append(value)
    values = sorted(values, key=lambda x: x[1])
    return values

def print_conditions(cd: Path):
    path = cd / "Condition*.json"
    conditions = []
    for p in glob.glob(str(path)):
        with open(p) as f:
            condition = json.load(f)
            conditions.append(
                ("Condition:",
                 condition['recordedDate'],
                 condition['clinicalStatus']['text'],
                 condition['verificationStatus']['text'],
                 condition['code']['text'],
                 )
            )
    cs = sorted(conditions, key=lambda x: x[1])
    for c in cs:
        print(c)

def print_value(w: tuple):
    print(F"{w[0]:10}: {w[1]} - ", end="")
    values = w[2]
    if not isinstance(values, list):
        values = [values]
    for value in values:
        print(F" {value[0]:6.1f} {value[1]},", end="")
        # if w[2] == "kg":
        #     print(f": {w[1] * 2.2:6.1f}")
    print()

def print_values(ws: list[tuple]) -> NoReturn:
    for w in ws:
        print_value(w)


def parse_args():
    parser = argparse.ArgumentParser(description='Explore Kaiser Health Data')

    # Add verbose argument
    parser.add_argument('-v', '--vital', type=str,
        help='Print a vital statistic, like weight. Name has to match EXACTLY, "Weight" is not "weight".\nSome examples:\n'
                        +'SpO2, Weight, "Blood Pressure" (quotes are required, if the name has spaces in it).')
    parser.add_argument('-c', '--condition', action='store_true', help='Print all active conditions.')
    # Parse the command-line arguments
    args = parser.parse_args()
    return args.vital, args.condition

def go():
    vital, condition = parse_args()
    base = Path("export/apple_health_export")
    condition_path = base / "clinical-records"

    if condition:
        print_conditions(condition_path)

    if vital:
        ws = extract_all_values(condition_path, vital)
        print_values(ws)


if __name__ == "__main__":
    go()
