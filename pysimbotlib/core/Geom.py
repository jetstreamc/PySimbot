import math
from collections.abc import Generator, Iterable


class Geom:
    Point2D = tuple[float, float]  # (x, y)
    BBox = tuple[float, float, float, float]  # (x, y, w, h)
    Line = tuple[Point2D, Point2D]  # ((x,y), (x,y))

    @staticmethod
    def is_bbox_overlap(bbox1: BBox, bbox2: BBox) -> bool:
        x1, y1, w1, h1 = bbox1
        x2, y2, w2, h2 = bbox2
        if x1 + w1 < x2 or x2 + w2 < x1:
            return False
        if y1 + h1 < y2 or y2 + h2 < y1:
            return False
        return True

    @staticmethod
    def all_bounding_lines_generator(obstacle_bboxes: Iterable[BBox]) -> Generator[Line, None, None]:
        # meta is (x, y, w, h)
        for bbox in obstacle_bboxes:
            buttom_left = (bbox[0], bbox[1])
            buttom_right = (bbox[0] + bbox[2], bbox[1])
            top_left = (bbox[0], bbox[1] + bbox[3])
            top_right = (bbox[0] + bbox[2], bbox[1] + bbox[3])
            yield (buttom_left, buttom_right)
            yield (buttom_right, top_right)
            yield (top_right, top_left)
            yield (top_left, buttom_left)

    @staticmethod
    def line_segment_intersect(p1: Point2D, p2: Point2D, p3: Point2D, p4: Point2D) -> Point2D | None:
        # ref: http://www.cs.swan.ac.uk/~cssimon/line_intersection.html
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        x4, y4 = p4
        denominator = (x4 - x3) * (y1 - y2) - (x1 - x2) * (y4 - y3)
        # not parallel lines
        if denominator != 0:
            ta = ((y3 - y4) * (x1 - x3) + (x4 - x3) * (y1 - y3)) / denominator
            tb = ((y1 - y2) * (x1 - x3) + (x2 - x1) * (y1 - y3)) / denominator
            # segment has intersection
            if 0 <= ta <= 1 and 0 <= tb <= 1:
                return (x1 + ta * (x2 - x1), y1 + ta * (y2 - y1))
        return None

    @staticmethod
    def line_segment_circle_intersect(
        p1: Point2D, p2: Point2D, center: Point2D, radius: float
    ) -> tuple[None, None] | tuple[Point2D, None] | tuple[Point2D, Point2D]:
        x1, y1 = p1
        x2, y2 = p2
        xc, yc = center
        a = (x2 - x1) ** 2 + (y2 - y1) ** 2
        b = 2 * ((x2 - x1) * (x1 - xc) + (y2 - y1) * (y1 - yc))
        c = (x1 - xc) ** 2 + (y1 - yc) ** 2 - radius**2
        discriminant = b**2 - 4 * a * c
        if discriminant < 0:
            return (None, None)
        elif discriminant == 0:
            t = -b / (2 * a)
            return ((x1 + t * (x2 - x1), y1 + t * (y2 - y1)), None)
        else:
            t1 = (-b - math.sqrt(discriminant)) / (2 * a)
            t2 = (-b + math.sqrt(discriminant)) / (2 * a)
            return ((x1 + t1 * (x2 - x1), y1 + t1 * (y2 - y1)), (x1 + t2 * (x2 - x1), y1 + t2 * (y2 - y1)))

    @staticmethod
    def distance(p1: Point2D, p2: Point2D) -> float:
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    @staticmethod
    def is_circle_rect_intersect(
        circle_center: Point2D, circle_radius: float, rect_center: Point2D, rect_width: float, rect_height: float
    ) -> bool:
        # for more info: https://stackoverflow.com/a/402010
        dx = abs(circle_center[0] - rect_center[0])
        dy = abs(circle_center[1] - rect_center[1])

        rect_half_width = 0.5 * rect_width
        rect_half_height = 0.5 * rect_height

        # check outside rect
        if dx > (rect_half_width + circle_radius) or dy > (rect_half_height + circle_radius):
            return False

        # check completely inside or overlap on some edge
        if dx <= rect_half_width or dy <= rect_half_height:
            return True

        # check corner
        corner_distance_sq = (dx - rect_half_width) ** 2 + (dy - rect_half_height) ** 2
        return corner_distance_sq <= circle_radius**2
