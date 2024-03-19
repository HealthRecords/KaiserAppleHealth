from pathlib import Path
import argparse

from health import yield_observation_files, \
    list_categories, list_vitals, do_vital, list_prefixes, print_medicines, print_conditions, print_procedures


# TODO Finish interactive/menu user interface. Observations is just getting started. Should this be a separate main?
# TODO Should I forget the interactive UI and make a django version?
# TODO For interactive mode, I need to be consistent about print, plot, and active/inactive.
# TODO like medicines, conditions should have an option to print inactive.
# TODO print_condition and print_medicines should be generalized and combined.
# TODO Do we want to have an option to process multiple or all stats in one run?
# TODO Should be able to graph anything with a value quantity and a date.

def parse_args():
    parser = argparse.ArgumentParser(description='Explore Kaiser Health Data - Text Menu',
                                     epilog='Example usage: python text_ui.py')

    parser.add_argument('--after', type=str,
                        help='YYYY-MM-DD format date. Only include dates after this date when using --stat.')
    parser.add_argument('--plot',  action=argparse.BooleanOptionalAction,
                        help='Plots the vital statistic selected with --stat.')
    parser.add_argument('--print', action=argparse.BooleanOptionalAction,
                        help='Prints the vital statistic selected with --stat.')
    parser.add_argument('--csv-format', action=argparse.BooleanOptionalAction,
                        help='Format printed output as csv')

    args = parser.parse_args()
    return args


def menu_show(choices: list[str]):
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

def menu_observation(data_dir: Path, args):
    """
    Observations are anything measured. Test results, measurements of height or weight, etc.

    :param data_dir:
    :param args:
    :return:
    """
    list_cat, dict_cat, file_count = list_categories(data_dir, False, one_prefix=None)
    while (option := menu_show(list_cat))[0] != -1:
        option_number, category = option
        vitals = list_vitals(yield_observation_files(data_dir), category)
        vital_list = [k for k in vitals.keys()]
        while (choices := menu_show(vital_list))[0] != -1:
            choice_number, choice_string = choices
            do_vital(data_dir, choice_string, args.after, True, True, args.csv_format,
                     category_name=category)
        print("You want information about ", option[1])
        # print("Would you like to print or plot this?")
    return

def menu_main(condition_path: Path, args) -> None:
    """
    display menus on the command line

    :param args:
    :param condition_path:
    :return: No Return
    """
    print()
    options = list(list_prefixes(condition_path).keys())
    while (var := menu_show(options))[0] != len(options):
        value = var[1]
        match value:
            case "quit":
                return
            case "Observation":
                menu_observation(condition_path, args)
            case "MedicationRequest":
                include_inactive, v = menu_show(["Active Medicines", "All Medicines"])
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
    args  = parse_args()
    base = Path("export/apple_health_export")
    condition_path = base / "clinical-records"

    menu_main(condition_path, args)
    return

if __name__ == "__main__":
    go()
