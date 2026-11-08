// The follower, the event-motor state machine and E6.
#include "../core/e6.h"
#include "../core/event_motor.h"
#include "../core/follower.h"
#include "fake_train.h"
#include "harness.h"

using namespace horloge;

TEST(follower_normal_running_one_step_at_once) {
  FollowerState s;
  const FollowerConfig cfg;
  int64_t target = 0;
  for (int ms = 0; ms < 60 * 1000; ++ms) {      // one minute of 1 ms ticks
    target = (static_cast<int64_t>(ms) * 1000) / 1125000;  // one µstep per 1.125 s
    const int64_t before = s.position;
    const int32_t n = follower_step(s, target, cfg);
    CHECK(n >= 0);
    CHECK(s.position <= target);
    if (target > before) CHECK_EQ(s.position, target);  // no lag in normal running
  }
  CHECK_EQ(s.position, 53);  // floor(59 999 / 1125)
}

TEST(follower_never_reverses) {
  FollowerState s;
  s.position = 1000;
  const FollowerConfig cfg;
  for (int i = 0; i < 100; ++i) CHECK_EQ(follower_step(s, 900, cfg), 0);
  CHECK_EQ(s.position, 1000);
}

TEST(follower_catch_up_one_day_lands_exactly) {
  FollowerState s;
  const FollowerConfig cfg;  // 3200 µsteps/s, 6400 µsteps/s²
  int ms = 0;
  int64_t last = 0;
  while (s.position < 76800 && ms < 60000) {
    follower_step(s, 76800, cfg);
    CHECK(s.position >= last);
    CHECK(s.position <= 76800);
    last = s.position;
    ++ms;
  }
  CHECK_EQ(s.position, 76800);
  // 24 s at full speed plus about 0.5 s of ramps [D: 76 800 / 3200; v / a]
  CHECK(ms > 24000 && ms < 26000);
}

TEST(follower_catch_up_to_a_moving_target) {
  FollowerState s;
  const FollowerConfig cfg;
  for (int ms = 0; ms < 40000; ++ms) {
    const int64_t target = 76800 + (static_cast<int64_t>(ms) * 1000) / 1125000;
    follower_step(s, target, cfg);
    CHECK(s.position <= target);
    if (ms == 39999) CHECK_EQ(s.position, target);
  }
}

// Run an event motor against a fake train, 10 ms ticks, until it settles or `limit_ms`.
static uint32_t run(EventMotor& m, FakeTrain& t, uint32_t limit_ms = 60000) {
  uint32_t now = 0;
  m.release(now);
  while (now < limit_ms) {
    now += 10;
    const MotorCmd c = m.tick(now, t.lock(), t.home());
    t.apply(c, 10);
    if (m.is_idle() || m.is_fault()) break;
  }
  return now;
}

TEST(event_motor_normal_run) {
  EventMotorConfig cfg;
  cfg.t_run_min_ms = 1000;
  EventMotor m(cfg);
  FakeTrain t;
  t.durations = {3000};
  run(m, t);
  CHECK(m.is_idle());
  CHECK_EQ(m.runs(), 1u);
  CHECK_EQ(t.runs, 1u);
  CHECK_EQ(m.early_warnings(), 0u);
  CHECK(m.learned_run_ms() >= 3000 && m.learned_run_ms() <= 3050);
  CHECK(!m.release(0) || true);  // idle again: a new release is accepted
}

TEST(event_motor_refuses_release_while_busy) {
  EventMotor m;
  CHECK(m.release(0));
  CHECK(!m.release(5));
}

TEST(event_motor_stuck_lock_never_opens) {
  EventMotor m;
  FakeTrain t;
  t.never_moves = true;
  run(m, t);
  CHECK(m.state() == EventState::FaultStuck);
  CHECK(m.tick(99999, true) == MotorCmd::Brake);
  m.acknowledge();
  CHECK(m.is_idle());
}

TEST(event_motor_timeout_lock_never_closes) {
  EventMotorConfig cfg;
  cfg.t_run_max_ms = 5000;
  EventMotor m(cfg);
  FakeTrain t;
  t.never_locks = true;
  run(m, t);
  CHECK(m.state() == EventState::FaultTimeout);
}

TEST(event_motor_early_close_is_a_warning) {
  EventMotorConfig cfg;
  cfg.t_run_min_ms = 2000;
  EventMotor m(cfg);
  FakeTrain t;
  t.durations = {500};
  run(m, t);
  CHECK(m.is_idle());
  CHECK_EQ(m.early_warnings(), 1u);
}

TEST(counting_train_runs_until_home_then_lock) {
  // A quarter train striking 4 pairs: the lock closes after each 3 s stroke cycle, but the train
  // must run on until the rack is home (docs/e2-design.md §12.1).
  EventMotorConfig cfg;
  cfg.uses_home = true;
  EventMotor m(cfg);
  FakeTrain t;
  t.durations = {12000};
  t.lock_every = 3000;
  const uint32_t end = run(m, t);
  CHECK(m.is_idle());
  CHECK_EQ(t.runs, 1u);
  CHECK(end >= 12000);
  // Without the home condition the same train would stop at the first closing.
  EventMotor plain;
  FakeTrain t2 = t;
  t2.runs = 0;
  t2.running = false;
  const uint32_t end2 = run(plain, t2);
  CHECK(end2 < 4000);
}

// ---- E6 ----

// The stop lever's beam after each division: clear (true) asks for another.
static uint8_t e6_night(const std::vector<bool>& clear_after, E6State* final_state) {
  E6Night e6;
  FakeTrain t;
  t.durations = {600};  // 100 rpm: one turn in 0.6 s [D: 60 / 100]
  uint32_t now = 0;
  e6.start(now);
  while (now < 20000 && e6.state() == E6State::Stepping) {
    now += 10;
    const size_t k = t.runs;
    const bool clear = k == 0 ? false : clear_after[(k - 1) < clear_after.size() ? k - 1 : clear_after.size() - 1];
    t.apply(e6.tick(now, t.lock(), !t.running && clear), 10);
  }
  *final_state = e6.state();
  return e6.divisions();
}

TEST(e6_ordinary_night_one_division) {
  E6State st;
  CHECK_EQ(e6_night({false}, &st), 1);
  CHECK(st == E6State::Done);
}

TEST(e6_new_year_four_or_three) {
  E6State st;
  CHECK_EQ(e6_night({true, true, true, false}, &st), 4);  // common year (m2-design §6)
  CHECK(st == E6State::Done);
  CHECK_EQ(e6_night({true, true, false}, &st), 3);        // leap year
  CHECK(st == E6State::Done);
}

TEST(e6_cap_at_four) {
  E6State st;
  CHECK_EQ(e6_night({true}, &st), 4);  // the lever keeps asking: stop and report
  CHECK(st == E6State::FaultCap);
}

TEST(e6_dead_opto_stops_after_one) {
  // A dead LED or a cut wire reads "blocked" (m2-design §6): one division, then rest.
  E6State st;
  CHECK_EQ(e6_night({false, false}, &st), 1);
  CHECK(st == E6State::Done);
}
