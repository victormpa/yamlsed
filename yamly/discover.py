import os

from yamly.patch import Patch
from yamly.template import Template

PATCH_SUFFIX = ".patch.yaml"


def discover(path: str, depth: int = None) -> dict:
    """
    Discover YAML files in the given path and return a tree mirroring the directory layout.

    Directories become nested dicts; YAML files are loaded as Template instances,
    except ``{name}.patch.yaml`` files which are loaded as Patch instances.

    :param path: The path to discover YAML files in.
    :param depth: The depth to discover YAML files in.
    :return: A tree of directories and loaded YAML templates and patches.
    """

    if depth is None:
        depth = float("inf")

    if depth == 0:
        return {}

    return _discover_dir(os.path.normpath(path), depth)


def _discover_dir(path: str, depth: int) -> dict:
    if depth == 0:
        return {}

    tree = {}
    next_depth = depth - 1 if depth != float("inf") else float("inf")

    for entry in sorted(os.listdir(path)):
        full_path = os.path.join(path, entry)
        if os.path.isdir(full_path):
            subtree = _discover_dir(full_path, next_depth)
            if subtree:
                tree[entry] = subtree
        elif entry.endswith(PATCH_SUFFIX):
            tree[entry] = Patch.load(full_path)
        elif entry.endswith(".yaml"):
            tree[entry] = Template.load(full_path)

    return tree
