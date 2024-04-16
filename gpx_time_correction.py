from bs4 import BeautifulSoup
from random import uniform, random
import uuid
import argparse
import os
import shutil

base_speed = 13  # basic speed km/h
point_delta_a, point_delta_b = 0.0000, 0.00005  # Lat lon spread
accuracy_s = "random:2.0:6.0"  # GPS meters accuracy for lockito

def rand_speed():
    r = random()
    if r < 0.6:
        return base_speed
    elif r < 0.8:
        return base_speed - 1
    else:
        return base_speed + 1

def main(path: str, out: str):
    base_file = open("./res/start.txt", "r", encoding="utf-8")
    base = base_file.read().replace("<name>", f"<name>{uuid.uuid4()}")
    base_file.close()
    end_file = open("./res/end.txt", "r", encoding="utf-8")
    end = end_file.read()
    end_file.close()

    wpts = ""
    trksegs = "\n  <trk>"

    with open(path, "r", encoding="utf-8") as in_file:
        raw_data = in_file.read()

    soup = BeautifulSoup(raw_data, "xml")

    points = list()

    for point in soup.find_all("trkpt"):
        points.append(
            {
                "lat": float(point["lat"]) + uniform(point_delta_a, point_delta_b),
                "lon": float(point["lon"]) + uniform(point_delta_a, point_delta_b),
                "altitude": point.find("ele").text,
            }
        )

    for point in points:
        wpts += f"""
      <wpt lat="{point['lat']}" lon="{point['lon']}">
        <extensions>
          <lockito:address>{uuid.uuid4()}</lockito:address>
        </extensions>
      </wpt>"""


    for i in range(0, len(points) - 1):
        p1 = points[i]
        p2 = points[i + 1]
        trksegs += f"""
        <trkseg>
          <trkpt lat="{p1['lat']}" lon="{p1['lon']}"/>
          <trkpt lat="{p2['lat']}" lon="{p2['lon']}"/>
          <extensions>
            <lockito:speed>fixed:{rand_speed()}</lockito:speed>
            <lockito:accuracy>{accuracy_s}</lockito:accuracy>
            <lockito:altitude>fixed:{p1['altitude']}</lockito:altitude>
          </extensions>
        </trkseg>"""

    trksegs += "\n  </trk>\n"

    with open(out, "w", encoding="utf-8", newline="\n") as out_file:
        out_file.write(base)
        out_file.write(wpts)
        out_file.write(trksegs)
        out_file.write(end)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base_file", type=str, help="Base gpx file to randomize", required=True)
    parser.add_argument("--number", type=int, help="Number of out randomized files", required=True)

    args = parser.parse_args()

    if os.path.isdir("./out"):
        shutil.rmtree("./out")

    os.mkdir("./out")

    path = args.base_file

    for i in range(1, args.number + 1):
        out = f"./out/out_{i}.gpx"
        main(path, out)

