from typing import List, Tuple, Union

from .describe import OPI
from .utils import hue_dist

__all__ = ["find_largest", "find_by_solidity", "find_by_hue"]


def find_largest(objs: List[OPI]) -> OPI:
    """Find largest object.

    Args:
        objs (List[OPI]): List of objects.

    Returns:
        OPI: Largest object.
    """
    # TODO: Filter away large object whose color is too close to blue?
    # I had to mess up the filtering to get gate to detect consistently, so
    # we can combine other tricks to filter out artifacts due to that.
    if len(objs) == 0:
        return None
    return max(objs, key=lambda x: x.area)


def find_by_solidity(objs: List[OPI], sol: float, thres: float = 0.1) -> OPI:
    """Find target by solidity.

    Args:
        objs (List[OPI]): List of objects.

    Returns:
        OPI: Gate object.
    """
    if len(objs) == 0:
        return None
    target = min(objs, key=lambda x: abs(x.solidity - sol))
    if abs(target.solidity - sol) > thres:
        return None
    return target


def find_by_hue(
    objs: List[OPI],
    color: Union[int, Tuple[int, int, int]],
    thres: Union[int, Tuple[int, int, int]] = 15,
) -> OPI:
    """Find target by hue.

    Args:
        objs (List[OPI]): List of objects.
        color (int | tuple): Target hue. If tuple, target saturation & value too.
        thres (int | tuple): Hue difference threshold. If tuple, filter by saturation & value too.

    Returns:
        OPI: Target.
    """
    is_hue = isinstance(color, int)
    assert (
        isinstance(thres, int) if is_hue else isinstance(color, tuple)
    ), "Color & thres must have same type."

    objs = [o for o in objs if o.color is not None]
    if len(objs) == 0:
        return None

    if is_hue:

        def diff(o):
            return hue_dist(o.color[0], color)
    else:

        def diff(o):
            return (
                hue_dist(o.color[0], color[0]),
                abs(o.color[1] - color[1]),
                abs(o.color[2] - color[2]),
            )

    scores = [(o, diff(o)) for o in objs]
    target, score = min(scores, key=lambda x: x[1] if is_hue else sum(x[1]))

    if is_hue and score > thres:
        return None

    if not is_hue and any(s > t for s, t in zip(score, thres)):
        return None

    return target
