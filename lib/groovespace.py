from html import escape
from typing import Any, Iterable, Sequence

def show_beat(beats: Sequence[Sequence[Any]],
              col_classes : Sequence[Sequence[Any]] | None = None,
              row_classes : Sequence[Any]           | None = None,
              table_class : str = "divisions" ) -> str:
    """
    Render a 2D HTML table from `beats`, using `col_classes` for per-cell CSS classes.

    - beats[y][x]: cell text (any type; converted to string).
    - col_classes[y][x]: CSS class string (used if truthy and not None).
      If col_classes is None or missing indices, no class attribute is added.

    Returns a complete <table class="divisions">…</table> string.
    """

    col_classes and interpolate2d(col_classes)
    row_classes and interpolate2d(row_classes)

    # Determine max columns across all beat rows (supports ragged input)
    max_cols = max((len(row) for row in beats), default=0)

    html_parts: list[str] = []
    html_parts.append( f'<table class="{table_class}">' )

    for y, row in enumerate(beats):
        if row_classes is not None and y < len(row_classes):
            crow = row_classes[y]
            html_parts.append( f"<tr class=\"{crow}\">")
        else:
            html_parts.append("<tr>")

        for x in range(max_cols):
            # Cell content
            if x < len(row):
                cell_text = escape(str(row[x]))
            else:
                cell_text = ""  # pad short rows with empty cells

            # Resolve class from col_classes if present/valid
            klass_attr = ""
            if col_classes is not None and y < len(col_classes):
                krow = col_classes[y]
                if x < len(krow):
                    k = krow[x]
                    if k is not None:
                        k_str = str(k).strip()
                        if k_str:
                            klass_attr = f' class="{escape(k_str)}"'

            html_parts.append(f"<td{klass_attr}>{cell_text}</td>")
        html_parts.append("</tr>")

    html_parts.append("</table>")

    return "".join(html_parts)

def interpolate2d(array2d):
    # Replace matching variable names with their values, but skip None
    for i, row in enumerate(array2d):
        if row is None:
            continue
        for j, val in enumerate(row):
            if val is None:
                continue
            if val in globals():           # variable name exists
                value = globals()[val]
                if value is not None:      # skip replacing with None
                    array2d[i][j] = value

def split2d(text):
    return [ line.split() for line in text.strip().split("\n") ]

ROW1="first r1"
ROW2="first r2"
ROW3="first r3"
ROW4="first r4"

G1="first g1"
G2="first g2"
G3="first g3"
G4="first g4"
B1="first b1"
B2="first b2"
B3="first b3"
B4="first b4"
R1="first r1"
R2="first r2"
R3="first r3"
R4="first r4"

g1="g1"
g2="g2"
g3="g3"
g4="g4"
b1="b1"
b2="b2"
b3="b3"
b4="b4"
r1="r1"
r2="r2"
r3="r3"
r4="r4"

N0="first"
n0=None
N=None
n=None

