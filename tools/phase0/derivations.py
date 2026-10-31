#!/usr/bin/env python3
"""Phase 0 derived numbers.

Every number tagged [D] in the Phase 0 docs (mechanism-inventory, envelope, architecture,
decisions) comes from this script, so it can be re-run and checked. Standard library only.

Run:  python3 tools/phase0/derivations.py
"""
from fractions import Fraction as F
import math

SCALE = 8
DAY = 86400.0


def section(title):
    print(f"\n## {title}")


# --- 1. Schwilgué's published ratios (reference-notes: CLEA, LEF) ----------------------
section("1. Schwilgué ratios (inputs from reference-notes.md)")
P = F(156 * 188 * 269, 9 * 10 * 10)
Y = P / 24  # tropical year in days (the printed expression is 24x the year)
print(f"P = 156*188*269/(9*10*10) = {float(P):.6f}; P/24 = {float(Y):.6f} d")
planets = {
    "Mercury": F(44 * 134, 240 * 102),
    "Venus": F(17 * 221, 197 * 31),
    "Mars": F(95 * 213, 203 * 53),
    "Jupiter": F(157 * 232, 96 * 32),
    "Saturn": F(161 * 212, 58 * 20),
}
for name, f in planets.items():
    print(f"  {name:8s} period = Y x {float(f):.6f} = {float(Y * f):10.3f} d")
lunar_turns = F(312, 24) * (1 - F(83 * 14, 122 * 196))
synodic = Y / lunar_turns
print(f"  lunar turns/yr = {float(lunar_turns):.6f}; synodic month = {float(synodic):.6f} d")

# Sidereal day from Schwilgué's tropical year (LEF): 365 d 5 h 48 min 48 s
Ys = F(31556928, 86400)
sid_ratio = Ys / (Ys + 1)
sid_day_s = float(sid_ratio) * DAY
print(f"  sidereal/mean day ratio = Y/(Y+1) = {float(sid_ratio):.10f} (= 164359/164809: "
      f"{sid_ratio == F(164359, 164809)})")
print(f"  sidereal day = {sid_day_s:.4f} s = {int(sid_day_s // 3600)} h "
      f"{int(sid_day_s % 3600 // 60)} min {sid_day_s % 60:.4f} s")
lunar_day_h = 24 * float(synodic) / (float(synodic) - 1)
print(f"  mean lunar day = 24 h x S/(S-1) = {lunar_day_h:.4f} h = 24 h {(lunar_day_h - 24) * 60:.2f} min")

# --- 2. Scale conversions ----------------------------------------------------------------
section("2. 1:8 conversions")
for label, mm in [
    ("case height 18 m", 18000), ("case width 7.70 m", 7700), ("case width 8.60 m", 8600),
    ("main dial 2.30 m", 2300), ("Apostle 18 in (457.2 mm)", 457.2),
    ("old calendar ring 2.92 m (second clock?)", 2920),
    ("1821 computus model 150 x 200 x 60 mm (NOT scaled: model is not part of the clock)", 0),
]:
    if mm:
        print(f"  {label:45s} -> {mm / SCALE:8.1f} mm")
dial = 2300 / SCALE
print(f"  day pitch on 287.5 mm circle = pi*287.5/365.2422 = {math.pi * dial / 365.2422:.3f} mm")
print(f"  day pitch on 366 equal sectors at 287.5 mm = {math.pi * dial / 366:.3f} mm")
print(f"  1 degree at radius {dial / 2:.2f} mm = {math.radians(1) * dial / 2:.2f} mm of arc")

# --- 3. Local mean time offsets ------------------------------------------------------------
section("3. Local mean time offsets (4 min of time per degree of longitude)")
for label, lon in [("Strasbourg cathedral 7.7506 E", 7.7506), ("Bordeaux 0.57 W", -0.57)]:
    off = lon * 4
    noon_cet = 12 * 60 + 60 - off
    print(f"  {label:30s} LMT - UT = {off:+.2f} min; mean noon = {int(noon_cet // 60):02d}:"
          f"{noon_cet % 60:04.1f} CET, {int(noon_cet // 60) + 1:02d}:{noon_cet % 60:04.1f} CEST")

# --- 3b. Calendar ring (DA p. 27: 25 cm wide, circumference "passé 9 mètres") -----------
section("3b. Calendar ring from Description abrégée (DA p. 27)")
C_min = 9000.0  # mm, lower bound ("over 9 m")
D_min = C_min / math.pi
print(f"  diameter > {D_min:.0f} mm -> 1:8 > {D_min / SCALE:.1f} mm; width 250 mm -> {250 / SCALE:.2f} mm")
r = D_min / SCALE / 2
for n in (3, 4):
    chord = 2 * r * math.sin(math.radians(360 / n / 2))
    print(f"  {n} segments of {360 // n} deg: chord {chord:.0f} mm (bed 320 mm)")
dlon = 7.7506 - (-0.57)
print(f"  Strasbourg-Bordeaux longitude difference {dlon:.4f} deg = {dlon * 4:.2f} min of time")

# --- 3c. Dimensions from Ungerer 1921 (ELS) at 1:8 ---------------------------------------
section("3c. ELS (Ungerer 1921) dimensions at 1:8")
for label, mm in [("calendar ring outer 2.73 m", 2730), ("calendar ring width 21 cm", 210),
                  ("planetary circle 2.20 m", 2200), ("Moon globe 0.40 m", 400),
                  ("celestial sphere 0.84 m", 840), ("Sun hand 1 m", 1000),
                  ("Sun disc 9.3 mm", 9.3), ("Moon disc 9.1 mm", 9.1), ("shadow disc 24.3 mm", 24.3),
                  ("eclipse cam R 154.2 mm", 154.2), ("eclipse cam r 113.8 mm", 113.8)]:
    print(f"  {label:30s} -> {mm / SCALE:8.2f} mm")
print(f"  1 degree on the 1 m Sun hand = {math.radians(1) * 1000:.2f} mm (ELS: 17.45 mm); at 1:8 {math.radians(1) * 1000 / SCALE:.2f} mm")
print(f"  Sun disc check: 32 arcmin x 17.45 mm/deg = {32 / 60 * 17.45:.2f} mm")
r = 2730 / SCALE / 2
print(f"  2.73 m ring at 1:8 in 4 segments: chord {2 * r * math.sin(math.radians(45)):.0f} mm")

# --- 4. Equation of time (Meeus 1998, eq. 28.3, low-precision form) ------------------------
section("4. Equation of time extremes (Meeus 1998 eq. 28.3, epoch J2000 constants)")
e, eps = 0.016709, math.radians(23.4393)
yv = math.tan(eps / 2) ** 2
vals = []
for i in range(36525):
    d = i / 100.0
    L0 = math.radians((280.46646 + 0.9856474 * d) % 360)
    M = math.radians((357.52911 + 0.98560028 * d) % 360)
    E = (yv * math.sin(2 * L0) - 2 * e * math.sin(M) + 4 * e * yv * math.sin(M) * math.cos(2 * L0)
         - 0.5 * yv * yv * math.sin(4 * L0) - 1.25 * e * e * math.sin(2 * M))
    vals.append(math.degrees(E) * 4)  # minutes of time
print(f"  min {min(vals):+.2f} min, max {max(vals):+.2f} min "
      f"-> Sun hand correction range on a 24 h dial: {min(vals) / 4:+.2f} deg to {max(vals) / 4:+.2f} deg")
eoc_amp = math.degrees(2 * e) * 4  # first-order equation of centre in minutes of time
red_amp = math.degrees(yv) * 4      # first-order reduction to the equator
print(f"  first-order terms: equation of centre +/-{eoc_amp:.2f} min (period: anomalistic year); "
      f"reduction to equator +/-{red_amp:.2f} min (period: half tropical year)")

# --- 5. Gear sizes vs the H2D bed -----------------------------------------------------------
section("5. Largest spur wheel that fits the H2D bed (tip diameter = m*(z+2))")
for bed, label in [(320, "single nozzle, limiting axis 320 mm"), (300, "dual nozzle, 300 mm axis")]:
    for m in (1.0, 0.8, 0.6):
        zmax = math.floor(bed / m - 2)
        print(f"  {label:36s} m={m}: z_max = {zmax} (with 0 margin; keep ~5 mm brim margin)")
for z in (269, 281, 382, 420):
    print(f"  Schwilgué wheel z={z}: tip dia m1.0 = {1.0 * (z + 2):.0f} mm, m0.8 = {0.8 * (z + 2):.1f} mm")

# --- 6. Coaxial brass tube nesting (Albion-type 0.45 mm wall, 1 mm OD steps) -----------
section("6. Tube nesting: OD n mm, wall 0.45 mm -> ID n-0.9 mm")
stack = [3.0] + [n for n in range(4, 11)]
for inner, outer in zip(stack[:-1], stack[1:]):
    idd = outer - 0.9
    print(f"  {inner:4.1f} mm inside tube {outer} x 0.45 (ID {idd:.1f}): diametral clearance {idd - inner:.2f} mm")

# --- 7. Stepper resolution and catch-up --------------------------------------------------
section("7. Stepper resolution (200 full steps, 1/16 microstep = 3200 usteps/rev)")
usteps = 200 * 16
for label, motor_rev_per_h, red in [("time module: motor 1 rev/h direct", 1, 1),
                                     ("daily module: motor 1 rev/h, 24:1 to 1 rev/day", 1, 24)]:
    interval = 3600 / (usteps * motor_rev_per_h)
    out_deg = 360 / (usteps * red)
    print(f"  {label:45s}: ustep every {interval:.3f} s; output step {out_deg:.5f} deg "
          f"(= {out_deg / 360 * (DAY if red == 24 else 3600):.3f} s of displayed time)")
for rpm in (60, 120):
    speedup = rpm * 60  # motor rev/h vs 1 rev/h nominal
    print(f"  catch-up at {rpm} rpm motor = {speedup}x real time: 1 day outage in "
          f"{86400 / speedup:.0f} s; 30 days in {30 * 86400 / speedup / 60:.0f} min")
full_step_deg = 1.8
print(f"  power-up phase jump up to +/-2 full steps = +/-{2 * full_step_deg} deg at motor -> "
      f"{2 * full_step_deg / 24:.3f} deg at a 1 rev/day arbor = {2 * full_step_deg / 24 / 360 * DAY:.0f} s of time")

# --- 8. Case mass estimate (envelope / mounting) ----------------------------------------
section("8. Case mass estimate [E] (method: panel areas x thickness x density)")
H, W, Dp = 2.25, 1.0, 0.30
ply = 680  # kg/m3, birch plywood, typical published range ~650-700
areas = {"front (60% solid)": 0.6 * H * W, "back": H * W, "sides": 2 * H * Dp, "shelves (6)": 6 * W * Dp}
a = sum(areas.values())
m_ply = a * 0.012 * ply
print(f"  panels {a:.2f} m2 of 12 mm birch ply @ {ply} kg/m3 -> {m_ply:.0f} kg")
glass = H * W * 0.004 * 2500
acryl = H * W * 0.003 * 1190
print(f"  glazing {H * W:.2f} m2: 4 mm glass {glass:.1f} kg or 3 mm acrylic {acryl:.1f} kg")
print(f"  + mechanisms (printed ~10-20 kg, metal ~5 kg) -> total ~{m_ply + acryl + 15:.0f}-{m_ply + glass + 25:.0f} kg")
