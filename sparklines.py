"""
This is an independent file, to test sparkline generation.

https://www.markhneedham.com/blog/2017/09/23/python-3-create-sparklines-using-matplotlib/

Limits:
you can use a fixed value for the upper and lower limit of the value.True
    Date range should be from the lowest date of any  test,  to the highest date of any test.test_categories()
Need to figure out how to scale each sparkline separately
could also maybe use pygal, which sounds cool. But let's use matplotlib for now.

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

def sparkline(data_x_str: list[datetime], data_y: list[float], min_normal, max_normal):
    data_x = [datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ') for date in data_x_str]

    fig, axes = plt.subplots(1, 1, figsize=(10, 10))
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

def sparklines(incoming: list[list[Observation]]) -> list[str]:
    """
    todo we need to pass in x and y
    :param incoming:
    :return:
    """
    # data1 = [x*x for x in range(30)]
    # d1_min = 0.3 *(max(data1) - min(data1))
    # d1_max = 0.8 *(max(data1) - min(data1))
    # data2 = [x*x*x for x in range(30)]
    # d2_min = 0.5 *(max(data2) - min(data2))
    # d2_max = 0.65 *(max(data2) - min(data2))
    # data3 = [x for x in range(30)]
    # d3_min = 0.2 *(max(data3) - min(data3))
    # d3_max = 0.45 *(max(data3) - min(data3))
    #
    # x = sparkline(data1, d1_min, d1_max)
    # y = sparkline(data2, d2_min, d2_max)
    # z = sparkline(data3,  d3_min, d3_max)
    outgoing = []
    for index in range(0, len(incoming)):
        one_ob_list = incoming[index]
        data_x = [x.date for x in one_ob_list]
        data_y = [x.data[0].value for x in one_ob_list]
        d1_min = 0.3 * (max(data_y) - min(data_y))
        d1_max = 0.8 * (max(data_y) - min(data_y))
        x = sparkline(data_x, data_y, d1_min, d1_max)
        outgoing.append(x)

    return outgoing


def html_page(f: TextIO, incoming):
    print("""<!DOCTYPE html><html><head><meta charset="utf-8" /><body>""", file=f)
    print("<h1>Sparklines</H1>", file=f)
    sparks = sparklines(incoming)
    for imgtag in sparks:
        print(imgtag, file=f)
    print("""</body></html>""", file=f)

if __name__ == "__main__":
    base = Path("export/apple_health_export")
    condition_path = base / "clinical-records"
    vital='Weight'
    category_name = 'Vital Signs'
    ws = extract_all_values(yield_observation_files(condition_path), vital, category_name=category_name)

    with open("sparklines.html", "w") as fff:
        html_page(fff, [ws])
