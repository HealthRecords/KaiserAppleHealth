"""
This is an independent file, to test sparkline generation.

https://www.markhneedham.com/blog/2017/09/23/python-3-create-sparklines-using-matplotlib/

Limits:
you can use a fixed value for the upper and lower limit of the value.True
    Date range should be from the lowest date of any  test,  to the highest date of any test.test_categories()
Need to figure out how to scale each sparkline separately
could also maybe use pygal, which sounds cool. But let's use matplotlib for now.

TODO: I need normal range for every possible test. It looks like what I want is in Observation-*.json files,
      as referenceRange. It's in 2707 out of 4541 files. Next step is to pass in a hard coded range, and plot
      those, then I can worry about getting the actual numbers.
"""
import base64
from io import BytesIO
from typing import TextIO
from matplotlib import pyplot as plt

def sparkline(data: list[float], min_normal, max_normal):
    fig, axes = plt.subplots(1, 1, figsize=(2, 0.5))
    axes.axis('off')
    plt.axhspan(min_normal, max_normal, color='green', alpha=0.3)
    axes.plot(data)
    img = BytesIO()
    plt.savefig(img)
    img.seek(0)
    plt.close()

    # fig.show()
    return '<img src="data:image/png;base64,{}"/>'.format(base64.b64encode(img.read()).decode())

def sparklines() -> list[str]:
    data1 = [x*x for x in range(30)]
    d1_min = 0.3 *(max(data1) - min(data1))
    d1_max = 0.8 *(max(data1) - min(data1))
    data2 = [x*x*x for x in range(30)]
    d2_min = 0.5 *(max(data2) - min(data2))
    d2_max = 0.65 *(max(data2) - min(data2))
    data3 = [x for x in range(30)]
    d3_min = 0.2 *(max(data3) - min(data3))
    d3_max = 0.45 *(max(data3) - min(data3))

    x = sparkline(data1, d1_min, d1_max)
    y = sparkline(data2, d2_min, d2_max)
    z = sparkline(data3,  d3_min, d3_max)

    return [x, y, z]
def html_page(f: TextIO):
    print("""<!DOCTYPE html><html><head><meta charset="utf-8" /><body>""", file=f)
    print("<h1>Sparklines</H1>", file=f)
    sparks = sparklines()
    for imgtag in sparks:
        print(imgtag, file=f)
    print("""</body></html>""", file=f)

if __name__ == "__main__":
    with open("sparklines.html", "w") as fff:
        html_page(fff)
