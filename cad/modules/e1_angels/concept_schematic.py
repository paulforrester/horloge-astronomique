"""E1 concept schematic (docs/img/e1/e1_concept.png). Not to final dimensions; numbers from docs/e1-design.md §2 [E].

Run: python cad/modules/e1_angels/concept_schematic.py docs/img/e1/e1_concept.png
"""
import sys, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Polygon, FancyArrowPatch, Arc

out = sys.argv[1]
fig = plt.figure(figsize=(15, 9.2))
gs = fig.add_gridspec(2, 3, height_ratios=[1.15, 0.85], hspace=0.32, wspace=0.18)
C_FIG, C_MECH, C_M1, C_NOTE = "#b08a5a", "#3060a0", "#999999", "#444444"

# ---- 1. front view of the gallery ----
ax = fig.add_subplot(gs[0, 0])
ax.set_title("1. Front: the lion gallery at 1:8 [E]", fontsize=11, loc="left")
ax.add_patch(Circle((0, 0), 60, fc="#e8dcc0", ec="k"))
ax.add_patch(Circle((0, 0), 52, fc="#222", ec="#c9a640", lw=2))
ax.text(0, 0, "M1\nØ104 dial\nØ120 bezel", ha="center", va="center", color="w", fontsize=8)
ax.add_patch(Rectangle((-82, -56), 164, 112, fill=False, ls="--", ec=C_M1))
ax.text(0, -76, "M1 frame ±82 (dashed, behind)", ha="center", color=C_M1, fontsize=8)
for sx, lab in ((-1, "A1 bell genie"), (1, "A2 hourglass genie")):
    x = 86 * sx
    ax.add_patch(Rectangle((x - 22, -12), 44, 26, fc="#d9c7a8", ec="k"))   # printed plinth
    ax.add_patch(Rectangle((x - 16, 14), 32, 40, fc=C_FIG, ec="k"))         # body
    ax.add_patch(Circle((x, 64), 11, fc=C_FIG, ec="k"))                      # head
    ax.add_patch(Polygon([[x, 44], [x + 48 * sx, 70], [x + 30 * sx, 30]], fc="#d8a050", ec="k", alpha=.6))
    ax.add_patch(Rectangle((x - 22 + 14 * sx, -48), 44, 32, fill=False, ec=C_MECH, ls=":"))
    ax.text(x, 86, lab, ha="center", fontsize=8.5)
ax.add_patch(Polygon([[-94, 52], [-74, 52], [-78, 40], [-90, 40]], fc="#c9a640", ec="k"))  # bell
ax.plot([-108, -92], [26, 40], color="k", lw=2)                                           # sceptre
ax.add_patch(Polygon([[80, 66], [92, 66], [86, 58], [92, 50], [80, 50], [86, 58]], fc="#f0e8e0", ec="k"))
ax.text(0, 74, "genies ≈ ±86 from the centreline", ha="center", fontsize=7.5)
ax.text(0, -98, "blue dotted: each genie's own small module,\nbehind the figure, on the internal frame",
        ha="center", color=C_MECH, fontsize=8)
ax.set_xlim(-150, 150); ax.set_ylim(-108, 100); ax.set_aspect("equal"); ax.axis("off")

# ---- 2. bell genie ----
ax = fig.add_subplot(gs[0, 1])
ax.set_title("2. A1: the sceptre flicks up at the bell (front)", fontsize=11, loc="left")
ax.add_patch(Polygon([[10, 60], [40, 60], [34, 44], [16, 44]], fc="#c9a640", ec="k"))
ax.plot([25, 25], [60, 70], color="k", lw=3); ax.text(44, 62, "real bell Ø≈20,\nheld by its handle", fontsize=8)
P = np.array([-20, 20.0])
ax.add_patch(Circle(P, 2.5, fc="w", ec="k", zorder=5))
ax.text(-64, 30, "shoulder arbor\n(front–back, through\nthe figure's back)", fontsize=8)
for ang, st, a in ((10, "-", 1), (-25, "--", .5)):
    t = np.radians(ang); tip = P + 42 * np.array([np.cos(t), np.sin(t)])
    ax.plot(*zip(P, tip), color="k", lw=3, ls=st, alpha=a)
ax.text(4, 32, "strike", fontsize=8); ax.text(14, -6, "cocked", fontsize=8, alpha=.7)
ax.add_patch(FancyArrowPatch((22, -2), (24, 16), connectionstyle="arc3,rad=.3", arrowstyle="->", mutation_scale=12))
# behind: lever, cam, spring
ax.add_patch(Circle((-20, -30), 12, fc="none", ec=C_MECH, lw=1.5))
ax.plot([-20, -12], [-30, -42], color=C_MECH)
ax.text(-4, -34, "snail cam, behind,\n1 turn per stroke", color=C_MECH, fontsize=8)
ax.plot([-20, -20], [20, -18], color=C_MECH, ls=":")
ax.plot(np.linspace(-46, -24, 20), -14 + 2 * np.sin(np.linspace(0, 12 * np.pi, 20)), color=C_MECH)
ax.text(-62, -8, "spring", color=C_MECH, fontsize=8)
ax.text(-62, -72, "Cue → the cam draws the arm down a little (≈ 0.2 s [E]),\nthen drops it: the spring flicks the sceptre "
        "up, it strikes\nand rebounds off a banking stop. The lock switch stops\nthe motor at rest (arm low, as in the photograph).",
        fontsize=8, color=C_NOTE)
ax.set_xlim(-65, 75); ax.set_ylim(-86, 78); ax.set_aspect("equal"); ax.axis("off")

# ---- 3. hourglass ----
ax = fig.add_subplot(gs[0, 2])
ax.set_title("3. A2: Scotch yoke, rack and pinion (behind)", fontsize=11, loc="left")
ax.add_patch(Circle((0, 0), 8, fc="none", ec=C_MECH, lw=1.5)); ax.plot([0, 0], [0, 8], color=C_MECH, lw=2)
ax.add_patch(Circle((0, 8), 1.4, fc=C_MECH))
ax.text(-38, -16, "crank r ≈ 7.5, half a turn\nper event, forward only", color=C_MECH, fontsize=8)
ax.add_patch(Rectangle((-30, 6.5), 60, 3, fc="none", ec=C_MECH))  # yoke slot
ax.plot([30, 30], [8, 34], color=C_MECH, lw=2)
for y in np.arange(18, 34, 1.6): ax.plot([30, 32], [y, y], color=C_MECH, lw=1)
ax.text(34, 12, "rack, stroke\n2r ≈ 15", color=C_MECH, fontsize=8)
ax.add_patch(Circle((37, 27), 4.8, fc="none", ec=C_MECH)); ax.text(44, 30, "pinion 12T m0.8\nØ9.6: 15 mm = ½ turn", color=C_MECH, fontsize=8)
ax.add_patch(Polygon([[33, 50], [41, 50], [37, 44], [41, 38], [33, 38], [37, 44]], fc="#f0e8e0", ec="k"))
ax.plot([37, 37], [27, 38], color="k", ls=":"); ax.text(44, 42, "glass on the pinion's arbor,\nturns in the facade plane", fontsize=8)
th = np.linspace(0, 360, 200)
axi = ax.inset_axes([0.12, 0.0, 0.55, 0.28])
axi.plot(th, 90 * (1 - np.cos(np.radians(th))), color="k"); axi.set_xticks([0, 180, 360]); axi.set_yticks([0, 180])
axi.axvspan(0, 180, color="#dde8f5"); axi.text(60, 140, "event n", ha="center", fontsize=7)
axi.text(300, 140, "event n+1", ha="center", fontsize=7)
axi.set_xlabel("crank °", fontsize=7); axi.set_ylabel("glass °", fontsize=7); axi.tick_params(labelsize=7)
ax.set_xlim(-40, 80); ax.set_ylim(-75, 55); ax.set_aspect("equal"); ax.axis("off")

# ---- 4. timeline of the hour ----
ax = fig.add_subplot(gs[1, :])
ax.set_title("4. On the hour, seconds from the genie's first stroke [S: Paul's cadence; D: E2 §11.3 at ≈ 32 rpm, E]", fontsize=11, loc="left")
rows = ["E2 walk", "A1 genie", "E2 old man", "A2 glass", "E2 Death"]
for i, r in enumerate(rows): ax.text(-12.5, -i, r, va="center", fontsize=9)
ax.barh(0, 8.7, left=-8.7, color="#cccccc"); ax.text(-4.3, 0, "walk out 8.7", ha="center", va="center", fontsize=8)
ax.barh(0, 13.8, left=9 + 1.0, color="#cccccc"); ax.text(17, 0, "hold 1.8 + walk on 10.3 + slip 1.7", ha="center", va="center", fontsize=8)
for k in range(4):
    ax.plot([3 * k], [-1], "v", color=C_MECH, ms=11); ax.plot([3 * k + 1], [-2], "v", color=C_FIG, ms=11)
ax.text(10.3, -1, "cue → stroke ≤ 0.3 s [E]", fontsize=8, va="center", color=C_MECH)
ax.barh(-3, 3.0, left=10.0, color=C_MECH, alpha=.6); ax.text(13.2, -3, "half turn ≈ 3 s [E], from the old man's last stroke [S: DA p. 51]", va="center", fontsize=8)
ax.plot([23.8, 23.8], [-3.6, -4.4], color="k", ls="--"); ax.text(24.2, -4, "Death starts (12 strokes at noon)", va="center", fontsize=8)
ax.set_xlim(-13, 44); ax.set_ylim(-4.7, 0.7); ax.set_yticks([]); ax.set_xlabel("s")
for s in ("left", "right", "top"): ax.spines[s].set_visible(False)

fig.text(0.01, 0.005, "Schematic only, not to final dimensions. Positions scaled on Paul's photograph IMG_0766 [E ±20 %].", fontsize=8, color=C_NOTE)
fig.savefig(out, dpi=110, bbox_inches="tight")
