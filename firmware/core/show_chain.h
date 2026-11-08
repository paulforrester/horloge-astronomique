// The show chain for one quarter, in DA's order (docs/firmware-design.md §7.3).
//
//   T − lead : E2 walk, phase A (the age walks out; `lead` is learned, nominal 8.7 s)
//   T        : E2 quarter train (n pairs); each E2 cue fires one E1 bell-genie stroke
//   quarters locked : E2 walk, phase B (the age walks on); at :00 also the E1 hourglass
//   at :00, walk locked and hourglass done : E2 hour train (Death)
//   at noon, Death locked : E3 procession; each E3 cue (figures 4, 8, 12) fires one E4 crow
//
// Rule 4: the release flags on M1b gate each step. A step whose window is not open is skipped and
// reported. A motor that faults counts as done, so the rest of the chain goes on where it can.
// When E2 is silent (quiet hours) the hourglass runs at T on the hour, and the noon show at T.
// The hour train (and so its home opto) is used only at :00: at other quarters a rack left down by
// a silent walk is not a fault (docs/e2-design.md §12.4).
#pragma once
#include <cstdint>

#include "event_motor.h"
#include "schedule.h"

namespace horloge {

enum Motor : uint8_t { kWalk, kQuarters, kHours, kBell, kHourglass, kProcession, kRooster,
                       kChainMotors };

struct ChainInputs {
  bool lock[kChainMotors] = {true, true, true, true, true, true, true};  // closed at rest
  bool home[kChainMotors] = {};    // home optos (the counting trains)
  bool cue_e2 = false;             // E2's cue switch (before each age stroke)
  bool cue_e3 = false;             // E3's cue switch (figures 4, 8, 12)
  bool win_quarter = false;        // M1b release windows (docs/m1-design.md §9.4)
  bool win_hour = false;
  bool win_noon = false;
};

struct ChainPlan {
  Quarter q;
  bool e2 = true;          // false in quiet hours or with the show off (F8)
  bool hourglass = true;
  bool noon_show = true;
  // Phase A's duration: nominal 1.80 + 5.16 + 1.72 s (docs/e2-design.md §11.3). The controller
  // passes its running mean of measured phase-A runs once it has some (§7.1).
  uint32_t walk_lead_ms = 8680;
};

enum ChainFault : uint8_t {
  kNoFault = 0,
  kWindowQuarter = 1 << 0,  // the quarter flag was not seen when the walk was due
  kWindowHour = 1 << 1,
  kWindowNoon = 1 << 2,
  kMotorFault = 1 << 3,     // a motor faulted during the chain
  kCueMissed = 1 << 4,      // a cue came while its follower was still busy
};

class ShowChain {
 public:
  // `t_ms`: the quarter instant on the controller's ms clock.
  void begin(const ChainPlan& plan, int64_t t_ms);
  // One tick; ticks every motor and fills `cmds`.
  void tick(int64_t now_ms, const ChainInputs& in, EventMotor* motors, MotorCmd* cmds);

  bool active() const { return active_; }
  uint8_t faults() const { return faults_; }
  uint8_t bell_strokes() const { return bell_strokes_; }
  uint8_t crows() const { return crows_; }
  // The order in which the steps were released, for tests and the log.
  const Motor* order() const { return order_; }
  uint8_t order_len() const { return order_len_; }
  // When the walk is due to start (T − lead).
  int64_t walk_start_ms() const { return walk_start_ms_; }

 private:
  bool release(Motor m, int64_t now_ms, EventMotor* motors);
  // Locked: the train has reached its lock (braking or at rest) or faulted. The next step may start
  // while the last one is still braking.
  static bool settled(const EventMotor& m) {
    return m.is_idle() || m.is_fault() || m.state() == EventState::Braking;
  }

  ChainPlan plan_{};
  int64_t t_ms_ = 0, walk_start_ms_ = 0;
  bool active_ = false;
  bool started_[kChainMotors] = {};
  uint8_t walk_runs_ = 0;
  bool prev_cue_e2_ = false, prev_cue_e3_ = false;
  uint8_t faults_ = 0, bell_strokes_ = 0, crows_ = 0;
  Motor order_[16] = {};
  uint8_t order_len_ = 0;
};

}  // namespace horloge
