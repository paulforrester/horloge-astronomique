"""M2 E6, the calendar ring's nightly drive (finger, star and pinion; the crank-and-pawl fallback),
and the stop lever at the pointer: the rules the design must keep (docs/m2-design.md §6)."""
import math

import pytest

bd = pytest.importorskip("build123d")
pytest.importorskip("shapely")

from cad.modules.m2_main_dial import calendar as CAL  # noqa: E402
from cad.modules.m2_main_dial import calendar_logic as L  # noqa: E402
from cad.modules.m2_main_dial import e6 as E  # noqa: E402


def test_ring_carries_one_gear_tooth_per_division():
    assert E.RING.teeth == L.N == 368
    assert E.RING.tip_radius == pytest.approx(CAL.LIP[1])                # tips at the lip's old edge
    assert E.RING.root_radius > CAL.LIP[0] + 4                           # the lip keeps a solid band
    assert E.PINION.teeth == E.STAR_N                                    # one star point = one ring tooth


def test_pinion_is_phased_to_mesh_with_the_ring_at_rest():
    from shapely.geometry import Polygon
    from shapely import affinity
    ring = Polygon(E.RING.outline(flank_points=6)).buffer(0)
    for p in (0, 100, 307):
        r = affinity.rotate(ring, 180.0 - p * E.DIV, origin=(0, 0))
        S = E.star_xy()
        pin = lambda rot: affinity.translate(affinity.rotate(Polygon(E.PINION.outline(flank_points=6)), rot, origin=(0, 0)), *S)
        assert pin(E.pinion_rotation(p)).intersection(r).area < 1e-6, p           # meshed, with backlash
        assert pin(E.pinion_rotation(p) + 15.0).intersection(r).area > 0.1, p      # and really in mesh
        # at rest a star gap faces the finger
        g = (E.star_rotation(p) + 180.0 / E.STAR_N - E.PSI_E) % (360.0 / E.STAR_N)
        assert min(g, 360.0 / E.STAR_N - g) < 1e-6


def test_one_finger_turn_moves_the_star_one_point():
    # the jumper settles any push between 0.5 and 1.5 points to exactly one
    for depth in (-0.3, 0.0, 0.3):                  # finger depth error (mm)
        for phase in (-0.1, 0.0, 0.1):              # star rest phase error (points)
            travel, jam = E.finger_push(depth, phase, dth=1.0)
            assert not jam and 0.65 < travel < 1.45, (depth, phase, travel)
    assert E.finger_dwell() > 250.0                  # room for the motor to stop at home and coast


def test_star_jumper_and_its_wire():
    j = E.jumper_spring()
    assert j["stress_max"] < j["limit"]
    # it holds the star (so the ring) against the ring's friction, and settles each step
    R = E.RING.pitch_radius
    ring_torque_on_star = E.FRICTION_N * E.PINION.pitch_radius
    from cad.modules.m2_main_dial import setter as S
    g = E.jumper_geometry()
    hold = j["F_nose_rest"] * math.tan(math.radians(45) + math.atan(S.MU)) * g["nose_r"]
    settle = j["F_nose_rest"] * math.tan(math.radians(45) - math.atan(S.MU)) * g["nose_r"]
    assert hold > 5 * ring_torque_on_star and settle > 2 * ring_torque_on_star


def test_wires_clear_the_pivots_they_pass():
    # each wire is allowed to touch its own lever at the contact, so check the pivot boss explicitly
    g = E.jumper_geometry()
    for anchor, contact, pivot, d in ((g["anchor"], g["contact"], g["pivot"], E.JUMPER_WIRE_D),):
        ux, uy = contact[0] - anchor[0], contact[1] - anchor[1]
        n = math.hypot(ux, uy)
        w = (pivot[0] - anchor[0], pivot[1] - anchor[1])
        along = (w[0] * ux + w[1] * uy) / n
        assert math.hypot(w[0] - along * ux / n, w[1] - along * uy / n) >= 1.6 + d / 2 + 0.1
    (ax, az), (cx, cz) = E.SL_WIRE_ANCHOR, E.stop_wire_contact()
    px, pz = E.SL_PIVOT
    dx, dz = cx - ax, cz - az
    n = math.hypot(dx, dz)
    t = ((px - ax) * dx + (pz - az) * dz) / n
    assert math.hypot(ax + t * dx / n - px, az + t * dz / n - pz) >= 1.7 + E.SL_WIRE_D / 2 + 0.1


def test_pinion_strength():
    sf = E.pinion_safety()
    assert sf["daily"] > 4 and sf["new_year"] > 4 and sf["counter_normal"] > 4
    # the counter's step before a leap year (once in four years, about a second): >= 2 against the
    # allowable stress, which is already PLA's strength / 4. Paul accepted 2.65 here (PR #9, 4 Nov
    # 2026); the running minimum of 4 holds for every other load.
    assert sf["counter_leap"] > 2


def test_loads_with_friction_and_the_bench_limits():
    # at MU 0.3 the loads are the documented ones; each friction term grows with mu
    base = E.mesh_loads()
    assert abs(base["counter_leap"] - E.mesh_loads(0.3)["counter_leap"]) < 1e-9
    for k in base:
        assert E.mesh_loads(0.2)[k] < base[k] < E.mesh_loads(0.5)[k], k
    lim = E.bench_limits()
    assert all(est <= limit + 1e-9 for est, limit, _, _ in lim.values())
    assert abs(E.pinion_capacity() / lim["counter_normal"][1] - 4.0) < 1e-9
    assert abs(lim["counter_leap"][1] - base["counter_leap"]) < 1e-9


def test_stop_lever_climbs_the_s_bumps_and_its_spring():
    s = E.stop_spring()
    assert s["stress_max"] < s["limit"]
    assert E.stop_lever_rotation() < math.radians(15)
    # the tip overlaps both halves of track S by at least 1 mm, at rest and when pushed back (it
    # then moves inward with the lever's turn), and stays clear of the witness flag and the counter pin
    arm = E.SL_PIVOT[1] - (E.SL_RIM_Z - 1.0)
    shift = abs(arm) * E.stop_lever_rotation()
    for dx in (0.0, -shift):
        lo, hi = E.SL_TIP_X[0] + dx, E.SL_TIP_X[1] + dx
        for half in (CAL.S_INNER, CAL.S_OUTER):
            assert min(hi, half[1]) - max(lo, half[0]) > 1.0, (dx, half)
    assert E.SL_TIP_X[0] > CAL.TRACK_WITNESS[1] + 0.5 and E.SL_TIP_X[1] < CAL.R_PIN - 1.25 - 0.05


def _stop():
    return {n: sh for n, sh, _ in E.stop_parts()}


def test_stop_opto_reads_the_lever():
    # TCST1202 [S: Vishay 83764]: the vane blocks the beam at rest and clears it with the lever back, by
    # at least 0.3 mm beyond the 0.5 mm slit's edges either way; it covers the slit's 3.8 mm depth
    st = E.opto_states()
    assert st["margin_rest"] >= 0.3 and st["margin_back"] >= 0.3, st
    assert st["y_cover"]
    assert st["travel"] > E.OPTO["slit_w"] + E.OPTO["resolution"]
    # pushed back, the lever (and its vane) still clears the opto and the bridge
    import build123d as bd
    P = _stop()
    th = math.degrees(E.stop_lever_rotation())
    back = P["stop_lever"].rotate(bd.Axis((E.SL_PIVOT[0], 0, E.SL_PIVOT[1]), (0, 1, 0)), -th)
    assert (back & P["stop_opto"]).volume < 1e-6 and (back & P["stop_bridge"]).volume < 1e-6
    tail = bd.Box(20, 6, 20, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.CENTER)).moved(
        bd.Location((E.OPTO_X, 2.0, -12)))                     # beside the tail (|y| <= 1.5): the vane only
    rise = (back & tail).bounding_box().min.Z - (P["stop_lever"] & tail).bounding_box().min.Z
    assert abs(rise - st["travel"]) < 0.05                                                # the vane rose
    # the output: IC min 1 mA at IF 20 mA, against 0.33 mA for a 10 kΩ pull-up at 3.3 V
    assert E.OPTO["ic_min"] >= 3 * 3.3 / 10.0


def test_stop_wire_is_glued_in_the_bridge_and_free_beyond():
    import build123d as bd
    from cad.lib import parts
    P = _stop()
    wire, bridge = P["stop_lever_spring"], P["stop_bridge"]
    assert (wire & bridge).volume < 1e-6                     # in its glue hole and channel, never cut
    (kx, kz), (ax, az), (fx, fz), u = E.stop_wire_line()
    ang = -math.degrees(math.atan2(u[1], u[0]))

    def sleeve(p0, length, d):
        return parts.rod(d, length).rotate(bd.Axis.Y, 90).rotate(bd.Axis.Y, ang).moved(bd.Location((p0[0], 0.0, p0[1])))
    # the clamped length is surrounded by the bridge (a 1.2 mm sleeve is at least 90 % in material) ...
    d = E.SL_WIRE_D
    ring_vol = math.pi / 4 * (1.2 ** 2 - (d + 0.05) ** 2) * E.WIRE_CLAMP
    assert (sleeve((kx, kz), E.WIRE_CLAMP, 1.2) & bridge).volume > 0.9 * ring_vol
    # ... and the free length is not: a 0.7 mm sleeve from the anchor to the arm touches nothing
    free = math.hypot(fx - ax, fz - az)
    assert (sleeve((ax, az), free, 0.7) & bridge).volume < 1e-6


def test_stop_pin_can_be_fitted():
    # the pin's hole runs through the bridge's width, so the pin can be pushed in, and out for service
    import build123d as bd
    P = _stop()
    probe = bd.Cylinder(0.5, 2 * E.BRIDGE_Y + 4, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(
        bd.Axis.X, 90).moved(bd.Location((E.SL_PIVOT[0], 0, E.SL_PIVOT[1])))
    assert (probe & P["stop_bridge"]).volume < 1e-6
    assert (P["stop_lever_pivot"] & P["stop_bridge"]).volume > 0.1          # pressed into both cheeks


@pytest.mark.parametrize("drive", ["star", "pawl"])
def test_every_wire_spring_is_glued_behind_its_anchor_and_free_over_its_design_length(drive):
    # the spring sums use the free length from the holder's face to the contact; the holder must not
    # cover any of it, and must hold WIRE_CLAMP of the wire behind the face
    import numpy as np
    from cad.lib.assembly import _mesh
    from cad.modules.m2_main_dial import setter as S
    a, _ = CAL.build(dates=False, e6=drive)
    wires = [("setter_detent_spring", "setter_detent_anchor", S.DETENT_WIRE_L, 0.5),
             ("satellite_detent_spring", "wheel_C_100", S.SAT_WIRE_L, 0.8),
             ("wheel_C_click_spring", "station_bracket", S.CLICK_WIRE_L, 0.8)]
    wires += {"star": [("e6_jumper_spring", "e6_bracket", E.JUMPER_WIRE_L, 0.8)],
              "pawl": [("ring_jumper_spring", "e6_bracket", E.RJ_WIRE_L, 0.8)]}[drive]
    for w, h, L, over in wires:
        v, _ = _mesh(a[w].shape, 0.02)
        v = np.asarray(v)
        c = v.mean(axis=0)
        u = np.linalg.svd(v - c)[2][0]
        t = (v - c) @ u
        total = t.max() - t.min()
        vi, _ = _mesh(a[w].shape & a[h].shape, 0.02)
        ti = (np.asarray(vi) - c) @ u
        lo, hi = ti.min() - t.min(), ti.max() - t.min()
        if hi > total / 2:
            lo, hi = total - hi, total - lo
        assert lo < 0.05 and abs(hi - S.WIRE_CLAMP) < 0.05, (w, lo, hi)
        assert abs(total - hi - over - L) < 0.05, (w, total - hi - over, L)


def test_pawl_fallback_steps_one_tooth():
    # variant "pawl": the hook's push, from the rest phase the ring jumper holds, settles to one tooth
    for phase, depth in ((-0.2, 0.0), (0.0, 0.0), (0.2, 0.0), (0.0, -0.2), (0.0, 0.2)):
        travel, jam = E.pawl_push(E.PAWL_REST_PHASE + phase, depth, dth=1.5)
        assert not jam and 0.6 < travel < 1.45, (phase, depth, travel)
    r = E.ring_jumper_spring()
    assert r["stress_max"] < r["limit"]


@pytest.mark.parametrize("drive", ["star", "pawl"])
def test_e6_parts_meet_only_the_teeth_as_the_ring_turns(drive):
    # every ring item passes E6 once a year: the bands of E6's parts that reach the ring may only
    # hold the ring's teeth (the segments), never the rocker, its detent, the pins or the sector
    from cad.lib import parts
    from cad.lib.assembly import _mesh
    a, _ = CAL.build(dates=False, e6=drive)
    readers = {"star": ["e6_pinion"], "pawl": ["e6_pawl", "ring_jumper"]}[drive]
    for name in readers:
        v, _ = _mesh(a[name].shape, 0.05)
        rs = [math.hypot(x, y) for x, y, _ in v]
        r0, r1 = min(rs), min(max(rs), CAL.R_OUT + 1.0)
        z0, z1 = v[:, 2].min(), v[:, 2].max()
        band = parts.disc(2 * r1, z1 - z0, bore=2 * r0, z0=z0)
        hits = set()
        for it in a.items:
            if it.group != "ring" or it.inside or it.name.startswith("ring_segment_"):
                continue
            bb = it.shape.bounding_box()
            if bb.max.Z < z0 or bb.min.Z > z1:
                continue
            if (it.shape & band).volume > 1e-3:
                hits.add(it.name)
        assert not hits, (name, hits)
