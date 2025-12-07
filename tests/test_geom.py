from pysimbotlib.core.Geom import Geom


def test_is_bbox_overlap():
    bbox1 = (0, 0, 10, 10)
    bbox2 = (5, 5, 10, 10)
    assert Geom.is_bbox_overlap(bbox1, bbox2)

    bbox3 = (20, 20, 10, 10)
    assert not Geom.is_bbox_overlap(bbox1, bbox3)


def test_line_segment_intersect():
    p1 = (0, 0)
    p2 = (10, 10)
    p3 = (0, 10)
    p4 = (10, 0)

    intersection = Geom.line_segment_intersect(p1, p2, p3, p4)
    assert intersection == (5.0, 5.0)

    # Parallel lines
    p5 = (0, 1)
    p6 = (10, 11)
    assert Geom.line_segment_intersect(p1, p2, p5, p6) is None


def test_distance():
    p1 = (0, 0)
    p2 = (3, 4)
    assert Geom.distance(p1, p2) == 5.0
    assert Geom.distance(p2, p1) == 5.0


def test_line_segment_circle_intersect():
    # Line passing through center
    p1 = (-10, 0)
    p2 = (10, 0)
    center = (0, 0)
    radius = 5.0

    intersections = Geom.line_segment_circle_intersect(p1, p2, center, radius)
    # Expect two intersection points: (-5, 0) and (5, 0)
    assert intersections is not None
    assert intersections[0] == (-5.0, 0.0) or intersections[1] == (-5.0, 0.0)
    assert intersections[0] == (5.0, 0.0) or intersections[1] == (5.0, 0.0)

    # Line tangent
    p3 = (-10, 5)
    p4 = (10, 5)
    intersections = Geom.line_segment_circle_intersect(p3, p4, center, radius)
    assert intersections[0] == (0.0, 5.0)
    assert intersections[1] is None

    # No intersection
    p5 = (-10, 6)
    p6 = (10, 6)
    assert Geom.line_segment_circle_intersect(p5, p6, center, radius) == (None, None)


def test_is_circle_rect_intersect():
    rect_center = (10, 10)
    rect_w = 10
    rect_h = 10
    # rect range: x[5, 15], y[5, 15]

    # Circle center inside rect
    assert Geom.is_circle_rect_intersect((10, 10), 1, rect_center, rect_w, rect_h)

    # Circle intersects edge
    assert Geom.is_circle_rect_intersect((4, 10), 2, rect_center, rect_w, rect_h)

    # Circle outside
    assert not Geom.is_circle_rect_intersect((0, 0), 1, rect_center, rect_w, rect_h)

    # Corner overlap
    # Top-right corner is (15, 15). Circle at (16, 16) with radius > sqrt(2) should overlap
    assert Geom.is_circle_rect_intersect((16, 16), 2, rect_center, rect_w, rect_h)
