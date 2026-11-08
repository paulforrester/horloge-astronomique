// The show chain in DA's order, against fake trains, and the persistence record.
#include <cstring>
#include <vector>

#include "../core/persist.h"
#include "../core/show_chain.h"
#include "fake_train.h"
#include "harness.h"

using namespace horloge;

struct Rig {
  EventMotor motors[kChainMotors];
  FakeTrain trains[kChainMotors];
  ShowChain chain;
  std::vector<int64_t> release_ms[kChainMotors];  // when each motor started
  bool windows = true;

  explicit Rig(uint8_t n) {
    EventMotorConfig counting;
    counting.uses_home = true;
    counting.t_run_max_ms = 60000;
    motors[kQuarters] = EventMotor(counting);
    motors[kHours] = EventMotor(counting);
    EventMotorConfig long_run;
    long_run.t_run_max_ms = 60000;
    motors[kProcession] = EventMotor(long_run);
    trains[kWalk].durations = {8680, 13830};   // e2-design §11.3
    trains[kQuarters].durations = {3000u * n};  // a pair every 3 s
    trains[kQuarters].lock_every = 3000;
    for (uint8_t i = 0; i < n; ++i) trains[kQuarters].cues.push_back(100 + 3000u * i);
    trains[kHours].durations = {36000};         // 12 strokes, one per 3 s
    trains[kHours].lock_every = 3000;
    trains[kBell].durations = {600};
    trains[kHourglass].durations = {3000};
    trains[kProcession].durations = {30000};
    trains[kProcession].cues = {9000, 18000, 27000};
    trains[kRooster].durations = {2000};
  }

  // Run from T − 10 s until the chain ends.
  void run(const ChainPlan& plan, int64_t t_ms, int64_t limit_ms = 200000) {
    chain.begin(plan, t_ms);
    bool was_running[kChainMotors] = {};
    for (int64_t now = t_ms - 10000; now < t_ms + limit_ms; now += 10) {
      ChainInputs in;
      for (int m = 0; m < kChainMotors; ++m) {
        in.lock[m] = trains[m].lock();
        in.home[m] = trains[m].home();
      }
      in.cue_e2 = trains[kQuarters].cue();
      in.cue_e3 = trains[kProcession].cue();
      in.win_quarter = in.win_hour = in.win_noon = windows;
      MotorCmd cmds[kChainMotors];
      chain.tick(now, in, motors, cmds);
      for (int m = 0; m < kChainMotors; ++m) {
        trains[m].apply(cmds[m], 10);
        const bool r = cmds[m] == MotorCmd::Run;
        if (r && !was_running[m]) release_ms[m].push_back(now);
        was_running[m] = r;
      }
      if (!chain.active() && now > t_ms) break;
    }
  }
};

static ChainPlan plan_for(uint8_t n, uint8_t hour12, bool noon) {
  ChainPlan p;
  p.q.n = n;
  p.q.hour12 = hour12;
  p.q.noon = noon;
  return p;
}

TEST(chain_noon_in_das_order) {
  Rig rig(4);
  const int64_t T = 1000000;
  rig.run(plan_for(4, 12, true), T);
  CHECK(!rig.chain.active());
  CHECK_EQ(rig.chain.faults(), 0);
  // Released in order: walk, quarters, the hourglass and the walk on, Death, the procession.
  const Motor want[] = {kWalk, kQuarters, kBell, kBell, kBell, kBell, kHourglass, kWalk,
                        kHours, kProcession, kRooster, kRooster, kRooster};
  CHECK_EQ(rig.chain.order_len(), sizeof(want) / sizeof(want[0]));
  for (size_t i = 0; i < sizeof(want) / sizeof(want[0]) && i < rig.chain.order_len(); ++i)
    CHECK_EQ(rig.chain.order()[i], want[i]);
  // The walk starts 8.68 s early; the first pair is struck at the quarter instant. A released
  // motor's first Run command comes one tick (here 10 ms) later.
  CHECK(rig.release_ms[kWalk].front() - (T - 8680) <= 10);
  CHECK(rig.release_ms[kQuarters].front() >= T && rig.release_ms[kQuarters].front() <= T + 20);
  CHECK_EQ(rig.chain.bell_strokes(), 4);
  CHECK_EQ(rig.chain.crows(), 3);
  // Death waits for the walk on and the hourglass.
  CHECK(rig.release_ms[kHours].front() >= rig.release_ms[kWalk].back() + 13830);
  CHECK_EQ(rig.trains[kWalk].runs, 2u);
}

TEST(chain_quarter_past_stops_after_the_walk_on) {
  Rig rig(1);
  rig.run(plan_for(1, 0, false), 500000);
  const Motor want[] = {kWalk, kQuarters, kBell, kWalk};
  CHECK_EQ(rig.chain.order_len(), 4);
  for (int i = 0; i < 4; ++i) CHECK_EQ(rig.chain.order()[i], want[i]);
  CHECK(rig.release_ms[kHours].empty());
  CHECK(rig.release_ms[kHourglass].empty());
}

TEST(chain_quiet_hours_only_the_hourglass_on_the_hour) {
  Rig rig(4);
  ChainPlan p = plan_for(4, 3, false);
  p.e2 = false;  // quiet hours: the ages, the genie and Death are silent (F6, PR #21)
  const int64_t T = 2000000;
  rig.run(p, T);
  CHECK_EQ(rig.chain.order_len(), 1);
  CHECK_EQ(rig.chain.order()[0], kHourglass);
  CHECK(rig.release_ms[kHourglass].front() >= T);
  CHECK(rig.release_ms[kWalk].empty());
}

TEST(chain_window_not_open_skips_e2) {
  Rig rig(4);
  rig.windows = false;  // the release flags on M1b were not seen (rule 4)
  rig.run(plan_for(4, 5, false), 3000000);
  CHECK(rig.chain.faults() & kWindowQuarter);
  CHECK(rig.release_ms[kWalk].empty());
  CHECK(rig.release_ms[kHours].empty());
  CHECK(!rig.chain.active());
}

TEST(chain_goes_on_after_a_bell_fault) {
  Rig rig(4);
  rig.trains[kBell].never_moves = true;  // the genie is jammed
  rig.run(plan_for(4, 7, false), 4000000);
  CHECK(rig.chain.faults() & kMotorFault);
  CHECK(!rig.release_ms[kHours].empty());  // Death still strikes
  CHECK(!rig.chain.active());
}

// ---- persistence ----

TEST(crc32_check_value) {
  const char* s = "123456789";
  CHECK_EQ(crc32(reinterpret_cast<const uint8_t*>(s), 9), 0xCBF43926u);
}

TEST(record_round_trip_and_corruption) {
  PersistRecord r;
  r.seq = 41;
  for (int i = 0; i < kAxes; ++i) {
    r.position[i] = 1000000000000LL * (i + 1) - 7;
    r.p_k[i] = -i;
    r.mscnt[i] = static_cast<uint16_t>(16 * i);
  }
  r.j = 1201;
  r.walk_phase = 1;
  r.e6_divisions = 3;
  r.ring_age = 2;
  r.faults = 0x80000001u;
  uint8_t buf[kRecordBytes];
  encode_record(r, buf);
  PersistRecord back;
  CHECK(decode_record(buf, back));
  CHECK_EQ(back.seq, 41u);
  CHECK_EQ(back.position[7], 8000000000000LL - 7);
  CHECK_EQ(back.p_k[3], -3);
  CHECK_EQ(back.mscnt[5], 80);
  CHECK_EQ(back.j, 1201);
  CHECK_EQ(back.ring_age, 2);
  CHECK_EQ(back.faults, 0x80000001u);
  buf[20] ^= 0x01;
  CHECK(!decode_record(buf, back));
}

TEST(record_newest_slot_and_torn_write) {
  PersistRecord a, b, out;
  a.seq = 10;
  b.seq = 11;
  b.j = 5;
  uint8_t sa[kRecordBytes], sb[kRecordBytes];
  encode_record(a, sa);
  encode_record(b, sb);
  CHECK(newest_record(sa, sb, out));
  CHECK_EQ(out.seq, 11u);
  CHECK_EQ(next_slot(sa, sb), 0);  // overwrite the older
  sb[kRecordBytes - 1] ^= 0xFF;     // the write to b was cut by a power loss
  CHECK(newest_record(sa, sb, out));
  CHECK_EQ(out.seq, 10u);
  CHECK_EQ(next_slot(sa, sb), 1);
  std::memset(sa, 0, sizeof sa);
  CHECK(!newest_record(sa, sb, out));
  // Sequence wrap-around.
  a.seq = 0xFFFFFFFFu;
  b.seq = 0;
  encode_record(a, sa);
  encode_record(b, sb);
  CHECK(newest_record(sa, sb, out));
  CHECK_EQ(out.seq, 0u);
}
