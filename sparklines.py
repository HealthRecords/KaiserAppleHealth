"""
This file generates a set of sparklines. Currrently hard coded.

https://www.markhneedham.com/blog/2017/09/23/python-3-create-sparklines-using-matplotlib/

Limits:
you can use a fixed value for the upper and lower limit of the value.True
    Date range should be from the lowest date of any  test,  to the highest date of any test.test_categories()
Need to figure out how to scale each sparkline separately
could also maybe use pygal, which sounds cool. But let's use matplotlib for now.

TODO: Need to match the date range across all sparklines, if I'm going to line them up.

TODO: I need normal range for every test we want to plot (I guess it's not required, just nice to have).
      It looks like what I want is in Observation-*.json files,
      as referenceRange. It's in 2707 out of 4541 files.
"""
import base64
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import TextIO

from matplotlib import pyplot as plt
import matplotlib.dates as mdates

from health import extract_all_values, yield_observation_files, Observation, StatInfo


def sparkline(data_x_str: list[str], data_y: list[float], graph_y_min, graph_y_max, normal_min, normal_max):
    data_x = [datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ') for date in data_x_str]

    fig, axes = plt.subplots(1, 1, figsize=(4, 1))
    # axes.axis('off')
    plt.axhspan(normal_min, normal_max, color='green', alpha=0.3)
    axes.set_ylim([graph_y_min, graph_y_max])
    axes.plot(data_x, data_y)

    # Calculate major ticks for x-axis
    years = mdates.YearLocator()
    plt.gca().xaxis.set_major_locator(years)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    img = BytesIO()
    plt.savefig(img)
    img.seek(0)
    plt.close()
    return '<img src="data:image/png;base64,{}"/>'.format(base64.b64encode(img.read()).decode())

def sparklines(incoming: list[list[Observation]]) -> list[tuple[str, str]]:
    """
    Generate a list of sparklines.
    :param incoming: a list of lists of Observations.
    :return: a list of (image tag, stat name) tuples
    """
    outgoing = []
    for index in range(0, len(incoming)):
        one_ob_list = incoming[index]
        if len(one_ob_list) == 0:
            continue

        data_x = [x.date for x in one_ob_list]
        data_y = [x.data[0].value for x in one_ob_list]  # TODO handle blood pressure and other multi-values stats.
        BASELINE_ZERO = True
        if BASELINE_ZERO:
            normal_min = 0.3 * (max(data_y))  # TODO: We need to get this from referenceRange
            normal_max = 0.8 * (max(data_y))
            baseline = 0
        else:
            normal_min = 0.3 * (max(data_y) - min(data_y))  # TODO: We need to get this from referenceRange
            normal_max = 0.8 * (max(data_y) - min(data_y))
            baseline = normal_min
        graph_y_min = 0
        graph_y_max = max(data_y)
        img_info = sparkline(data_x, data_y, graph_y_min, graph_y_max, normal_min, normal_max)
        outgoing.append((img_info, one_ob_list[0].name))

    return outgoing


def html_page(f: TextIO, incoming):
    """
    Generate HTML page for the sparklines
    :param f:
    :param incoming:
    :return:
    """
    print("""<!DOCTYPE html><html><head><meta charset="utf-8" /><body>""", file=f)
    print("<h1>Sparklines</H1>", file=f)
    sparks = sparklines(incoming)
    print("<table>", file=f)
    for imgtag, stat_name in sparks:
        print("<tr>", file=f)
        print("<td>", file=f)
        print(F"""{stat_name}""", file=f)
        print("</td><td>", file=f)
        print(imgtag, file=f)
        print("</td>\n", file=f)
        print("</tr>", file=f)
    print("</table>", file=f)
    print("""</body></html>""", file=f)

if __name__ == "__main__":
    base = Path("export/apple_health_export")
    condition_path = base / "clinical-records"

    # stats = ["Pulse", "Height", "Blood Pressure", "Weight", "Respirations", "SpO2", "Temperature"]
    # stats = ["SpO2"]
    stats = [StatInfo("Lab", "Potassium"), StatInfo("Vital Signs", "SpO2")]
    # stats = [StatInfo("Vital Signs", "SpO2")]
    # category_name = 'Vital Signs'

    stats_to_graph = []
    for vital in stats:
        ws = extract_all_values(yield_observation_files(condition_path), stat_info=vital)
        stats_to_graph.append(ws)

    with open("sparklines.html", "w") as fff:
        html_page(fff, stats_to_graph)
