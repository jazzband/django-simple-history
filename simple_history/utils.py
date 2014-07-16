import re
import difflib


REMOVED = 'removed'
ADDED = 'added'
UNCHANGED = 'unchanged'


def get_delta_sequences(a, b):
    delta_nodes = []
    try:
        a = re.split("(\W)", a)
        b = re.split("(\W)", b)
    except TypeError:
        if a != b:
            return [(REMOVED, a), (ADDED, b)]
        return [(UNCHANGED, b)]
    prev_a_start, prev_b_start, prev_len = (0, 0, 0)
    for block in difflib.SequenceMatcher(a=a, b=b).get_matching_blocks():
        a_start, b_start, length = block
        removed = "".join(a[prev_a_start + prev_len:a_start])
        added = "".join(b[prev_b_start + prev_len:b_start])
        same = "".join(b[b_start:b_start + length])
        if removed:
            delta_nodes.append((REMOVED, removed))
        if added:
            delta_nodes.append((ADDED, added))
        if same:
            delta_nodes.append((UNCHANGED, same))
        prev_a_start, prev_b_start, prev_len = block
    return delta_nodes
