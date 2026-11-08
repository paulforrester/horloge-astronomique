// Time law, summer time, the legal-time schedule and quiet hours.
#include <random>

#include "../core/schedule.h"
#include "../core/summer_time.h"
#include "../core/time_law.h"
#include "harness.h"

using namespace horloge;

// Reference instants from Python's datetime (independent of the code under test).
constexpr int64_t kSpring26 = 1774746000, kAutumn26 = 1792890000;
constexpr int64_t kSpring27 = 1806195600, kAutumn27 = 1824944400;

TEST(law_one_ustep_per_1125_ms) {
  CHECK_EQ(usteps_for(1124999), 0);
  CHECK_EQ(usteps_for(1125000), 1);
  CHECK_EQ(usteps_for(9 * kUsPerS), 8);
  CHECK_EQ(usteps_for(3600 * kUsPerS), kUstepsPerMotorRev);
  CHECK_EQ(usteps_for(86400 * kUsPerS), 24 * kUstepsPerMotorRev);  // 76 800 a day
  CHECK_EQ(usteps_for(-1), -1);                                     // floor, not truncation
}

TEST(law_exact_over_millennia_against_int128) {
  std::mt19937_64 rng(1);
  const int64_t span = 1000LL * 366 * 86400 * kUsPerS;  // a thousand years either way
  for (int i = 0; i < 200000; ++i) {
    const int64_t dt = static_cast<int64_t>(rng() % (2 * static_cast<uint64_t>(span))) - span;
    const __int128 num = static_cast<__int128>(dt) * kLawNum;
    __int128 ref = num / kLawDenUs;
    if (num % kLawDenUs != 0 && num < 0) ref -= 1;
    CHECK(usteps_for(dt) == static_cast<int64_t>(ref));
  }
}

TEST(law_mean_and_legal_offsets) {
  const int64_t epoch_us = kEpochUnixS * kUsPerS;
  // At the epoch, mean time is 31 min ahead of UTC: floor(1860 × 8 / 9) = 1653 µsteps.
  CHECK_EQ(target_usteps(TimeKind::Mean, epoch_us, 0, 0), 1653);
  // Legal time is CET at J = 0: one hour = 3200 µsteps.
  CHECK_EQ(target_usteps(TimeKind::Legal, epoch_us, 0, 0), 3200);
  // Spring +1 h and autumn +23 h.
  CHECK_EQ(target_usteps(TimeKind::Legal, epoch_us, 1, 0) - target_usteps(TimeKind::Legal, epoch_us, 0, 0), 3200);
  CHECK_EQ(target_usteps(TimeKind::Legal, epoch_us, 24, 0) - target_usteps(TimeKind::Legal, epoch_us, 1, 0), 73600);
  CHECK_EQ(target_usteps(TimeKind::Mean, epoch_us, 99, 7), 1653 + 7);  // J ignored, P_k added
}

TEST(summer_time_changes_2026_2027) {
  CHECK_EQ(eu_change_unix_s(2026, true), kSpring26);
  CHECK_EQ(eu_change_unix_s(2026, false), kAutumn26);
  CHECK_EQ(eu_change_unix_s(2027, true), kSpring27);
  CHECK_EQ(eu_change_unix_s(2027, false), kAutumn27);
}

TEST(summer_time_offset_and_j) {
  const SummerTimeConfig st;
  CHECK_EQ(legal_offset_s(kSpring26 - 1, st), 3600);
  CHECK_EQ(legal_offset_s(kSpring26, st), 7200);
  CHECK_EQ(legal_offset_s(kAutumn26 - 1, st), 7200);
  CHECK_EQ(legal_offset_s(kAutumn26, st), 3600);
  CHECK_EQ(summer_time_j(kEpochUnixS, st), 0);
  CHECK_EQ(summer_time_j(kSpring26 - 1, st), 0);
  CHECK_EQ(summer_time_j(kSpring26, st), 1);
  CHECK_EQ(summer_time_j(kAutumn26, st), 24);
  CHECK_EQ(summer_time_j(kAutumn27, st), 48);
}

TEST(summer_time_disabled_and_frozen) {
  SummerTimeConfig off;
  off.changes_enabled = false;
  CHECK_EQ(legal_offset_s(kSpring26 + 100, off), 3600);
  CHECK_EQ(summer_time_j(kAutumn27, off), 0);
  // The EU freezes the clocks on 1 June 2027, in summer time: they stay on CEST.
  SummerTimeConfig frozen;
  frozen.frozen_after_unix_s = 1811808000;  // 2027-06-01 00:00 UTC
  CHECK_EQ(summer_time_j(1827619200, frozen), 25);  // 1 Dec 2027: 24 + 1, no autumn change
  CHECK_EQ(legal_offset_s(1827619200, frozen), 7200);
}

TEST(schedule_quarters_and_noon) {
  const SummerTimeConfig st;
  Quarter q = quarter_at_or_after(1768478340, st);  // 15 Jan 2026 11:59 UTC = 12:59 CET
  CHECK_EQ(q.unix_s, 1768478400);
  CHECK_EQ(q.n, 4);
  CHECK_EQ(q.hour12, 1);
  CHECK(!q.noon);
  q = quarter_at_or_after(1768478400 - 3600, st);   // 11:00 UTC = 12:00 CET
  CHECK(q.noon);
  CHECK_EQ(q.hour12, 12);
  q = quarter_at_or_after(1782900000, st);           // 1 Jul 2026 10:00 UTC = 12:00 CEST
  CHECK(q.noon);
  q = quarter_at_or_after(1768478400 + 1, st);       // just after: 13:15 CET
  CHECK_EQ(q.n, 1);
  CHECK_EQ(q.hour12, 0);
  CHECK_EQ(q.legal_minute, 13 * 60 + 15);
}

TEST(schedule_on_change_nights) {
  const SummerTimeConfig st;
  // Spring: 01:00 UTC is 03:00 CEST; there is no 02:00 show.
  Quarter q = quarter_at_or_after(kSpring26, st);
  CHECK_EQ(q.hour12, 3);
  q = quarter_at_or_after(kSpring26 - 900, st);      // 00:45 UTC = 01:45 CET
  CHECK_EQ(q.legal_minute, 1 * 60 + 45);
  // Autumn: 00:45 UTC = 02:45 CEST, then 01:00 UTC = 02:00 CET (the hour runs twice).
  q = quarter_at_or_after(1792889100, st);
  CHECK_EQ(q.legal_minute, 2 * 60 + 45);
  q = quarter_at_or_after(kAutumn26, st);
  CHECK_EQ(q.hour12, 2);
  q = quarter_at_or_after(kAutumn26 + 1, st);
  CHECK_EQ(q.legal_minute, 2 * 60 + 15);
}

TEST(quiet_hours) {
  QuietConfig q;  // F6: 22:00-07:00, E2 silent
  CHECK(is_quiet(ShowClass::E2, 22 * 60, 0, q));
  CHECK(is_quiet(ShowClass::E2, 3 * 60, 0, q));
  CHECK(is_quiet(ShowClass::E2, 6 * 60 + 59, 0, q));
  CHECK(!is_quiet(ShowClass::E2, 7 * 60, 0, q));
  CHECK(!is_quiet(ShowClass::E2, 21 * 60 + 59, 0, q));
  CHECK(!is_quiet(ShowClass::Hourglass, 3 * 60, 0, q));
  q.quiet_now_until_unix_s = 1000;  // "quiet now"
  CHECK(is_quiet(ShowClass::E2, 12 * 60, 999, q));
  CHECK(!is_quiet(ShowClass::E2, 12 * 60, 1000, q));
  QuietConfig day;  // a window that does not cross midnight
  day.start_minute = 13 * 60;
  day.end_minute = 14 * 60;
  CHECK(is_quiet(ShowClass::E2, 13 * 60 + 30, 0, day));
  CHECK(!is_quiet(ShowClass::E2, 22 * 60, 0, day));
  day.end_minute = day.start_minute;  // no window
  CHECK(!in_quiet_window(13 * 60, day));
}

TEST(e2_ring_ages) {
  CHECK_EQ(age_for_quarter(1), 0);       // the child strikes :15
  CHECK_EQ(age_for_quarter(4), 3);       // the old man strikes :00
  CHECK_EQ(age_waiting_after(4), 0);     // then the child waits
  CHECK_EQ(age_waiting_after(1), 1);
  CHECK_EQ(kResyncTurns, 1);  // one silent walk, whatever age waits (e2-design §10.3)
}
