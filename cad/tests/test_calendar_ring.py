"""Calendar ring follow-up to PR #5: the sector clears the ring in both positions, and the dates
(Paul, PR #5: 2.2 mm days and dominical letters, 4 mm month names) sit where they should."""
import math

import pytest

bd = pytest.importorskip("build123d")
pytest.importorskip("shapely")

from cad.lib import lettering as T  # noqa: E402
from cad.modules.m2_main_dial import calendar as CAL  # noqa: E402
from cad.modules.m2_main_dial import calendar_logic as L  # noqa: E402


@pytest.mark.parametrize("leap", [False, True])
def test_sector_clears_the_ring_in_both_positions(leap):
    # PR #5 had the lug in the solid face in the leap position and the tab two divisions off its
    # slot; a blanket ring-sector contact allowance hid both
    ring, sector, feats = CAL.ring_and_sector(0, leap)
    assert (ring & sector).volume < 1e-6
    assert len(sector.solids()) == 1                       # foot, arm, lug and tab hang together
    for name, bump in feats.items():
        if name.startswith("S_bump"):
            assert (bump & sector).volume < 1e-6, name     # lug (outer half) never meets a bump (inner half)


def test_every_character_is_drawn():
    text = "".join(CAL.MONTHS) + "COMMENCEMENTDE L'ANNÉECOMMUNEABCDEFG0123456789"
    assert set(text) <= set(T.GLYPHS)


def test_dates_stay_on_the_face_and_in_their_bands():
    g = CAL.date_inlays(0, False)
    for name, (r_lo, r_hi) in (("face", (CAL.R_IN + 1.0, CAL.R_OUT - 1.0)),
                               ("sector", (CAL.R_IN + 1.2, CAL.R_OUT - 1.2)),
                               ("floor", (CAL.R_IN + 1.0, CAL.R_OUT - 1.0))):
        rs = [math.hypot(x, y) for p in getattr(g[name], "geoms", [g[name]]) for x, y in p.exterior.coords]
        assert r_lo < min(rs) and max(rs) < r_hi, name
    h, w, _ = CAL.DAY_TEXT
    assert h == 2.2 and CAL.MONTH_TEXT[0] == 4.0           # the approved sizes
    # each day's entry fits its division: glyph height plus stroke under the division width
    assert h + w < 2 * math.pi * (CAL.DAY_R0 - 6.0) / L.N


def test_first_of_january_is_A_and_the_pointer_reads_left_to_right():
    # ELS i4: "Au 1er janvier correspond la lettre A"; the day at the pointer (viewer's left) reads
    # inwards, i.e. left to right
    lines = T.radial("A", CAL.world_angle(L.SECTOR_COMMON_START, L.SECTOR_COMMON_START), CAL.DAY_R0, 2.2, 0.35, 0.35)
    xs = [x for line in lines for x, _ in line]
    assert max(xs) < -CAL.DAY_R0 + 2.0 and min(xs) >= -CAL.DAY_R0 - 1e-6


def test_inlays_are_cut_from_their_own_part():
    # base + inlay = the part without dates: the inlay is carved out of its own part, nothing more
    a, _ = CAL.build()
    plain, _ = CAL.build(dates=False)
    pairs = [(f"ring_segment_{k}", f"ring_text_{k}") for k in range(4)] + [("sector_jan_feb", "sector_text")]
    for base, ink in pairs:
        assert a[ink].inside == base and a[ink].print_set == a[base].print_set != ""
        assert a[ink].shape.volume > 50
        assert a[base].shape.volume + a[ink].shape.volume == pytest.approx(plain[base].shape.volume, abs=0.05)
        assert len(a[base].shape.solids()) == 1 and a[base].shape.is_valid
    # every printed calendar part meshes closed and manifold (Bambu Studio / lib3mf); PR #5's full-turn
    # wedges left a zero-width slit at the pointer that did not
    from cad.export_print import mesh_ok
    assert [i.name for i in a.items if i.printed and not mesh_ok(i.shape)] == []
