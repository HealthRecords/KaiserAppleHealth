"""
This is an independent file, to test sparkline generation.

https://www.markhneedham.com/blog/2017/09/23/python-3-create-sparklines-using-matplotlib/

Limits:
you can use a fixed value for the upper and lower limit of the value.True
    Date range should be from the lowest date of any  test,  to the highest date of any test.test_categories()
Need to figure out how to scale each sparkline separately
could also maybe use pygal, which sounds cool. But let's use matplotlib for now.

TODO: Need to match the date range across all sparklines, if I'm going to line them up.

TODO: My current plan is to make this the main program for generating sparklines, and have it call health.py functions
      to acquire the data to plot.
      First step, make this work on list[Observation]. Observation may need to me modified to include normal ranges.
TODO: I need normal range for every possible test. It looks like what I want is in Observation-*.json files,
      as referenceRange. It's in 2707 out of 4541 files. Next step is to pass in a hard coded range, and plot
      those, then I can worry about getting the actual numbers.
"""
import base64
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import TextIO
from matplotlib import pyplot as plt

from health import extract_all_values, yield_observation_files, Observation
import matplotlib.dates as mdates

def sparkline(data_x_str: list[str], data_y: list[float], min_normal, max_normal):
    data_x = [datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ') for date in data_x_str]

    fig, axes = plt.subplots(1, 1, figsize=(4, 1))
    # axes.axis('off')
    plt.axhspan(min_normal, max_normal, color='green', alpha=0.3)
    axes.plot(data_x, data_y)

    # Calculate major ticks for x-axis
    years = mdates.YearLocator()
    plt.gca().xaxis.set_major_locator(years)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    img = BytesIO()
    plt.savefig(img)
    img.seek(0)
    plt.close()

    # fig.show()
    return '<img src="data:image/png;base64,{}"/>'.format(base64.b64encode(img.read()).decode())

def sparklines(incoming: list[list[Observation]]) -> list[tuple[str, str]]:
    """
    todo we need to pass in x and y
    :param incoming:
    :return:
    """
    outgoing = []
    for index in range(0, len(incoming)):
        one_ob_list = incoming[index]
        if len(one_ob_list) == 0:
            continue

        data_x = [x.date for x in one_ob_list]
        data_y = [x.data[0].value for x in one_ob_list]
        d1_min = 0.3 * (max(data_y) - min(data_y))  # TODO: We need to get this from referenceRange
        d1_max = 0.8 * (max(data_y) - min(data_y))
        img_info = sparkline(data_x, data_y, d1_min, d1_max)
        outgoing.append((img_info, one_ob_list[0].name))

    return outgoing


def html_page(f: TextIO, incoming):
    print("""<!DOCTYPE html><html><head><meta charset="utf-8" /><body>""", file=f)
    print("<h1>Sparklines</H1>", file=f)
    sparks = sparklines(incoming)
    for imgtag, stat_name in sparks:
        print(F"""<h1>{stat_name}</h1>""", file=f)
        print(imgtag, file=f)
        print("<br>\n", file=f)
    print("""</body></html>""", file=f)

if __name__ == "__main__":
    base = Path("export/apple_health_export")
    condition_path = base / "clinical-records"

    stats = ["Pulse", "Height", "Blood Pressure", "Weight", "Respirations", "SpO2", "Temperature"]
    category_name = 'Vital Signs'

    stats_to_graph = []
    for vital in stats:
        ws = extract_all_values(yield_observation_files(condition_path), vital, category_name=category_name)
        stats_to_graph.append(ws)

    with open("sparklines.html", "w") as fff:
        html_page(fff, stats_to_graph)
