#!/usr/bin/env python3
"""Envelope estimates scaled from Schwilgué's workshop lithograph.

Source image: the plate "Horloge astronomique de la Cathédrale de Strasbourg, construite par
J.B. Schwilgué, 1838 à 1842" ("Des. & Lith. dans les Ateliers de M. Schwilgué", lith. Fasoli &
Ohlman), bound into Ch. Schwilgué, *Description abrégée*, 7th ed., 1854 (Google Books
LGYEyPW9ZWQC) and also into the 1844 edition. Public domain. The pixel coordinates below are for the
1092 x 1788 px extraction of that plate. `docs/img/plate_annotated.png` shows every measurement.

Method (docs/envelope.md §4):
  1. Check the drawing's proportions against five dimensions given by primary sources.
  2. Use the mean scale to estimate heights and sizes that no source gives.
  3. Uncertainty: the spread of the check scales (about ±3 %) plus about ±10 px of reading
     error, i.e. ±0.12 m at the original's scale.
These are [E] estimates. Photo measurements (envelope.md §4) should replace them.

Run:  python3 tools/envelope/plate_measurements.py
"""
SCALE = 8
BASE_Y = 1580   # px, bottom of the stone base (floor line)
TOP_Y = 38      # px, apex of the central crown finial

# --- 1. Checks: drawn size (px) vs sourced size (m) ---------------------------------------
checks = [
    # (feature, drawn px, sourced metres, source)
    ("case height, base to crown apex", BASE_Y - TOP_Y, 18.00, "ELS: 18 m 'le couronnement gothique compris'"),
    ("case width at the base (body, x 202-882)", 680, 7.70, "ELS: '7m,70 de largeur à la base'"),
    ("calendar ring outer diameter (Hough r 116.3)", 232.6, 2.73, "ELS: anneau de 2m,73 de diamètre extérieur"),
    ("apparent-time dial (inner edge of calendar ring)", 196, 2.30, "ELS: cadran de 2m,30"),
    ("planetary dial inner circle", 183, 2.20, "ELS: cercle de 2m,20"),
]
print("1. Drawing-proportion checks")
scales = []
for name, px, m, src in checks:
    s = px / m
    scales.append(s)
    print(f"   {name:48s} {px:7.1f} px / {m:5.2f} m = {s:5.1f} px/m   [{src}]")
mean = sum(scales) / len(scales)
spread = max(abs(s - mean) / mean for s in scales)
print(f"   mean scale {mean:.1f} px/m; max deviation {spread * 100:.1f} %")

# --- 2. Estimates for features no source gives ------------------------------------------
# (feature, centre y px (or None), size px (or None), size meaning)
features = [
    ("main dial centre (Hough)", 1434, None, ""),
    ("weekday chariots band", 1270, 145, "visible width"),
    ("lion gallery / mean-time dial centre", 1192, 67, "dial diameter"),
    ("planetary dial centre (Hough)", 1026, 234.8, "outer diameter of the zodiac band"),
    ("Moon globe centre", 845, None, "(size: use ELS 0.40 m)"),
    ("lower hall (four ages, Death) centre", 674, 125, "hall opening width"),
    ("upper hall (Christ, Apostles) centre", 572, 125, "hall opening width"),
    ("figures (Apostles, Death), drawn height", None, 60, "figure height [?]"),
    ("top of base stage (gallery floor)", 1192, 697, "base stage width x 183-880"),
    ("left (weight) tower top incl. rooster", 397, 147, "tower width x 215-362"),
    ("right (staircase) tower top", 616, 175, "tower width x 719-894"),
    ("central body", None, 318, "width x 381-699"),
]
print("\n2. Estimates [E] (scale %.1f px/m)" % mean)
print(f"   {'feature':44s} {'h above base':>13s} {'1:8':>8s}   {'size':>7s} {'1:8':>7s}")
for name, y, size, meaning in features:
    h = (BASE_Y - y) / mean if y is not None else None
    sz = size / mean if size is not None else None
    hs = f"{h:6.2f} m" if h is not None else "      -"
    h8 = f"{h * 1000 / SCALE:5.0f} mm" if h is not None else "      -"
    ss = f"{sz:5.2f} m" if sz is not None else "      -"
    s8 = f"{sz * 1000 / SCALE:4.0f} mm" if sz is not None else "     -"
    print(f"   {name:44s} {hs:>13s} {h8:>8s}   {ss:>7s} {s8:>7s}  {meaning}")
unc_rel = spread
unc_abs = 10 / mean
print(f"\n   uncertainty: about ±{unc_rel * 100:.0f} % of each value, plus ±{unc_abs:.2f} m reading error")
