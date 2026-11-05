"""M1 + M1b, the mean-time dial (docs/m1-design.md): geometry, trains, releases, clutch, dial."""
import math

import pytest

bd = pytest.importorskip("build123d")
pytest.importorskip("shapely")

from cad.modules.m1_time import dial as D
from cad.modules.m1_time import mechanism as M


@pytest.fixture(scope="module")
def built():
    a, data = M.build()
    return a, M.check(a, data)


def test_no_interference_and_everything_fits_the_bed(built):
    a, r = built
    assert r["interference"] == []
    assert r["bed_fit_single"] == [] and r["bed_fit_dual"] == []


def test_the_trains_are_the_spec_trains(built):
    # each motion work is 12/48 x 15/45 = 1/12 (M1.hour_hand, M1b.legal_hour_hand); the drives are 1:1;
    # the noon wheel turns once in 24 h: (12/54) x (12/64) of M1b's hourly shaft
    _, r = built
    pairs = {m["pair"].split(" (")[0]: m for m in r["meshes"]}
    assert (12 / 48) * (15 / 45) == pytest.approx(1 / 12)
    assert (12 / 54) * (12 / 64) == pytest.approx(1 / 24)
    assert pairs["cannon 12 / minute wheel 48"]["centre_distance"] == pairs["minute pinion 15 / hour wheel 45"]["centre_distance"]
    assert pairs["drive 45 / 45"]["centre_distance"] == pytest.approx(M.DRIVE_CD)


def test_every_mesh_is_engaged(built):
    """Pull each driven wheel 0.4 mm towards its driver: it must collide (no gap where a mesh is meant)."""
    a, r = built
    pos = r["positions"]
    checks = [("M1b_drive_45_noon_12", "silver_drive_45", "TB_M1b_motor", "centre"),
              ("M1_drive_45", "gilt_drive_45", "TA_M1_motor", "centre"),
              ("silver_cannon_12", "silver_minute_wheel_48", "centre", "SM_silver_motion_work"),
              ("gilt_cannon_12", "gilt_minute_wheel_48", "centre", "GM_gilt_motion_work"),
              ("silver_minute_pinion_15", "silver_hour_wheel_45", "SM_silver_motion_work", "centre"),
              ("gilt_minute_pinion_15", "gilt_hour_wheel_45", "GM_gilt_motion_work", "centre"),
              ("M1b_drive_45_noon_12", "noon_wheel_54_12_X", "TB_M1b_motor", "X_noon"),
              ("noon_wheel_54_12_X", "noon_wheel_64_N", "X_noon", "N_24h")]
    for drv, dvn, p1, p2 in checks:
        (x1, y1), (x2, y2) = pos[p1], pos[p2]
        d = math.hypot(x2 - x1, y2 - y1)
        moved = a[dvn].shape.moved(bd.Location((-(x2 - x1) / d * 0.4, -(y2 - y1) / d * 0.4, 0)))
        assert (a[drv].shape & moved).volume > 0.05, (drv, dvn)


def test_hand_order_front_to_back(built):
    # Paul, PR #11: gilt minute (front), silver minute, silver hour, gilt hour
    a, _ = built
    z = {n: a[n].shape.bounding_box().min.Z for n in
         ("hand_gilt_minute", "hand_silver_minute", "hand_silver_hour", "hand_gilt_hour")}
    assert z["hand_gilt_minute"] > z["hand_silver_minute"] > z["hand_silver_hour"] > z["hand_gilt_hour"] > 0.0


def test_releases_follow_legal_time_and_each_flag_meets_its_hall():
    # D14: the quarters at :15/:30/:45/:00 of legal time, the noon window at 12:00 legal time. A flag that
    # passed its Hall t minutes ago is back under it after its period; a quarter magnet k is 90 deg on
    for m in (0, 15, 30, 45):
        k = m // 15
        a_k = (M.flag_angle(M.HALL_ANG["quarter"], m, 60) - 90.0 * k) % 360    # magnet k's angle at m
        assert abs((a_k - M.HALL_ANG["quarter"]) % 360) < 1e-9 or abs((a_k - M.HALL_ANG["quarter"]) % 360 - 360) < 1e-9
    assert M.flag_angle(M.HALL_ANG["noon"], 0, 1440) == M.HALL_ANG["noon"]
    w = M.release_windows()
    assert w["quarter"] < 7.5 - 2.0                         # consecutive quarter windows never merge
    assert w["noon"] - w["noon_setting_error"] >= 10.0       # noon's hour flag falls inside the noon window
    assert w["noon"] + w["noon_setting_error"] <= 60.0 - 10.0  # 11:00 and 13:00 do not


def test_clutch_window_is_open_and_the_motor_has_margin():
    c = M.clutch_window()
    assert c["slip_min"] < c["slip_max"] and c["preload_min"] < c["preload_max"]
    assert c["motor_margin"] >= 10.0


def test_dial_two_colour_print():
    field, gilt = D.build()
    assert (field & gilt).volume < 1e-6 and gilt.volume > 100
    g = D.gilt_geometry()
    assert g.is_valid and max(abs(v) for v in g.bounds) < D.DIAL_D / 2 - 1.0
    for ch in "HQY":
        from cad.lib.lettering import GLYPHS
        assert ch in GLYPHS


def test_dial_lifts_off_the_front_on_its_magnets(built):
    """The motion works sit in front of the front plate, under the dial, so the dial must come off forwards:
    its four bezel magnets meet the four foot magnets face to face, and one foot is off the 90° pattern
    so the dial fits only one way round."""
    a, _ = built
    for k in range(4):
        fb, bb = a[f"magnet_foot_{k}"].shape.bounding_box(), a[f"magnet_bezel_{k}"].shape.bounding_box()
        assert fb.max.Z == pytest.approx(bb.min.Z, abs=1e-6)
        assert (fb.center().X, fb.center().Y) == pytest.approx((bb.center().X, bb.center().Y), abs=1e-6)
    gaps = sorted((M.FEET_ANG[(k + 1) % 4] - M.FEET_ANG[k]) % 360 for k in range(4))
    assert len(set(gaps)) > 1                                  # not invariant under any rotation but 360°
    for i in a.items:                                          # no screw or part reaches the dial from behind
        assert not i.name.startswith("dial_foot")


def test_pillar_screws_clear_the_motors_and_adapters():
    """An M3 nut (6.35 across corners) on each pillar screw, on the back plate's rear face, clears both motor
    adapters (which are wider than the motors)."""
    hx, hy = M.ADAPTER["w"] / 2, M.ADAPTER["h"] / 2
    for p in M.PILLARS:
        for c in (M.TA, M.TB):
            dx = max(abs(p[0] - c[0]) - hx, 0.0)
            dy = max(abs(p[1] - c[1]) - hy, 0.0)
            assert math.hypot(dx, dy) > 6.35 / 2 + 0.5, (p, c)


@pytest.mark.parametrize("tag", ["M1", "M1b"])
def test_each_motor_comes_out_from_behind_without_touching_a_gear(built, tag):
    """Option A (D16): the motor, its shaft and its adapter, withdrawn backwards, touch nothing at any point:
    the drive part stays behind, held by its post and the back plate, and the D-shaft slides out of it."""
    a, _ = built
    unit = [f"motor_{tag}", f"shaft_{tag}", f"adapter_{tag}"]
    others = [i for i in a.items if i.name not in unit]
    for dz in (-0.2, -3.0, -10.0, -30.0):
        for n in unit:
            moved = a[n].shape.moved(bd.Location((0, 0, dz)))
            mb = moved.bounding_box()
            for o in others:
                ob = o.shape.bounding_box()
                if mb.max.X < ob.min.X or ob.max.X < mb.min.X or mb.max.Y < ob.min.Y or ob.max.Y < mb.min.Y or \
                        mb.max.Z < ob.min.Z or ob.max.Z < mb.min.Z:
                    continue
                v = (moved & o.shape).volume
                assert v < 1e-3, f"{n} withdrawn {dz} mm hits {o.name} ({v:.3f} mm³)"


BODIES = {   # parts that move together along the axis
    "gilt minute (Ø3 arbor)": ["arbor_gilt_minute_3", "gilt_cannon_12", "gilt_drive_45", "gilt_wave_washer", "gilt_collar",
                               "hand_gilt_minute", "centre_cap"],
    "silver minute (OD 4)": ["tube_silver_minute_4", "silver_cannon_12", "silver_drive_45", "silver_wave_washer",
                             "silver_collar", "hand_silver_minute"],
    "silver hour (OD 5)": ["tube_silver_hour_5", "silver_hour_wheel_45", "hand_silver_hour"],
    "gilt hour (OD 6)": ["tube_gilt_hour_6", "gilt_hour_wheel_45", "hand_gilt_hour"],
    "gilt motion work": ["arbor_gilt_motion_work", "gilt_minute_wheel_48", "gilt_minute_pinion_15", "gilt_witness_disc",
                         "magnet_gilt_witness"],
    "silver motion work": ["arbor_silver_motion_work", "silver_minute_wheel_48", "silver_minute_pinion_15",
                           "magnet_silver_witness"],
    "M1 drive (TA)": ["M1_drive_45", "M1_index_disc", "magnet_M1_index"],
    "M1b drive (TB)": ["M1b_drive_45_noon_12", "M1b_flag_disc", "magnet_quarter_0", "magnet_quarter_1",
                       "magnet_quarter_2", "magnet_quarter_3", "magnet_hour"],
    "noon wheel X": ["noon_wheel_54_12_X"],
    "24 h wheel N": ["noon_wheel_64_N", "magnet_noon"],
}
ENDSHAKE_MAX = 0.45                 # E (0.3) plus a margin


@pytest.mark.parametrize("body", list(BODIES))
def test_every_moving_body_meets_a_stop_both_ways(built, body):
    """Endshake: slid ENDSHAKE_MAX forwards or backwards, each body must run into a part outside it (a stop).
    Only an increase in overlap counts, so the press fits and nested tubes that already overlap do not."""
    a, _ = built
    names = BODIES[body]
    members = [a[n] for n in names]
    others = [i for i in a.items if i.name not in names]

    def overlap(s, t):
        try:
            return (s & t).volume
        except Exception:
            return 0.0

    for dz in (ENDSHAKE_MAX, -ENDSHAKE_MAX):
        found = None
        for m in members:
            moved = m.shape.moved(bd.Location((0, 0, dz)))
            mb = moved.bounding_box()
            for o in others:
                ob = o.shape.bounding_box()
                if mb.max.X < ob.min.X or ob.max.X < mb.min.X or mb.max.Y < ob.min.Y or ob.max.Y < mb.min.Y or \
                        mb.max.Z < ob.min.Z or ob.max.Z < mb.min.Z:
                    continue
                if overlap(moved, o.shape) > overlap(m.shape, o.shape) + 1e-3:
                    found = (m.name, o.name)
                    break
            if found:
                break
        assert found, f"{body}: nothing stops it within {dz:+.2f} mm"
