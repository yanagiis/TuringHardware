import matplotlib.pyplot as plt
from process_translator import process_to_points


def main():
    test_fixed_point()
    test_spiral()
    test_circle()
    test_triangle()


def test_fixed_point():
    process = {
        "name": "FixedPoint",
        "coordinates": {
            "x": 10,
            "y": 15
        },
        "z": 180,
        "time": 60,
        "water": 30,
        "temperature": 70
    }

    points = process_to_points(process)
    draw_points(points, process['name'])


def test_spiral():
    process = {
        "name": "Spiral",
        "coordinates": {
            "x": 0,
            "y": 0
        },
        "z": {
            "from": 180,
            "to": 190
        },
        "radius": {
            "from": 5,
            "to": 40,
        },
        "cylinder": 5,
        "time": 60,
        "water": 30,
        "temperature": 70
    }

    points = process_to_points(process)
    draw_points(points, process['name'])


def test_circle():
    process = {
        "name": "Circle",
        "coordinates": {
            "x": 0,
            "y": 0
        },
        "radius": 30,
        "cylinder": 2,
        "z": 180,
        "time": 60,
        "water": 30,
        "temperature": 70
    }

    points = process_to_points(process)
    draw_points(points, process['name'])


def test_triangle():
    process = {
        "name": "Triangle",
        "coordinates": {
            "x": 0,
            "y": 0
        },
        "radius": 30,
        "cylinder": 5,
        "z": 180,
        "time": 60,
        "water": 30,
        "temperature": 80
    }

    points = process_to_points(process)
    draw_points(points, process['name'])


def draw_points(points, title):
    fig, ax = plt.subplots()
    for point in points:
        if point.x is not None and point.y is not None:
            ax.plot(point.x, point.y, '.')
    ax.set(xlabel='x (mm)', ylabel='y (mm)', title=title)
    ax.grid()
    plt.show()


if __name__ == '__main__':
    main()
