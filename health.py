import glob
import json
from pathlib import Path
from typing import NoReturn
import argparse

# TODO Print mix and max values?

def extract_values(cd: Path, sign_name: str) -> list[tuple]:
    path = cd / "Observation*.json"
    values = []
    for p in glob.glob(str(path)):
        with open(p) as f:
            condition = json.load(f)
            # if 'category' not in condition:
            #     print("X")
            # if 'text' not in condition['category']:
            #     print("Y")
            category_info = condition['category']
            assert isinstance(category_info, list)
            for ci in category_info:
                if ci['text'] == "Vital Signs":
                    if condition['code']['text'] == sign_name:
                        t = sign_name
                        d = condition['effectiveDateTime']
                        w = condition["valueQuantity"]["value"]
                        u = condition["valueQuantity"]["unit"]
                        values.append((t, d, w, u))
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
    print(F"{w[0]:10}: {w[1]} - {w[2]:6.1f} {w[3]}", end="")
    if w[3] == "kg":
        print(f": {w[2] * 2.2:6.1f}")
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
        ws = extract_values(condition_path, vital)
        print_values(ws)


if __name__ == "__main__":
    go()
