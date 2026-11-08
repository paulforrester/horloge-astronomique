// One event motor: a striking train run until its lock closes (docs/firmware-design.md §7.1).
//
//   IDLE --release--> LEAVING --lock opens--> RUNNING --lock closes--> BRAKING --> IDLE
//                        | t > t_leave             | t > t_run_max
//                        v                         v
//                   FAULT_STUCK               FAULT_TIMEOUT
//
// A counting train (E2's quarters and hours, docs/e2-design.md §12.1) also has a home opto: it
// runs until the opto is blocked (the rack is gathered home) and then stops at the next lock
// closing; lock closings before that pass through.
#pragma once
#include <cstdint>

namespace horloge {

enum class MotorCmd : uint8_t { Off, Run, Brake };

enum class EventState : uint8_t { Idle, Leaving, Running, Braking, FaultStuck, FaultTimeout };

struct EventMotorConfig {
  uint32_t t_leave_ms = 1000;    // the lock must open within this
  uint32_t t_run_min_ms = 0;     // a close earlier than this is logged as a warning
  uint32_t t_run_max_ms = 20000; // the lock must close within this ([E] 2 × nominal)
  uint32_t t_brake_ms = 100;
  bool uses_home = false;        // a counting train with a home opto
};

class EventMotor {
 public:
  explicit EventMotor(const EventMotorConfig& cfg = {}) : cfg_(cfg) {}

  // Start a run. Refused (returns false) unless idle.
  bool release(uint32_t now_ms);
  // Advance; returns the motor command for this tick.
  MotorCmd tick(uint32_t now_ms, bool lock_closed, bool home_blocked = false);
  // Clear a fault (after it was acknowledged).
  void acknowledge() { if (is_fault()) state_ = EventState::Idle; }

  EventState state() const { return state_; }
  bool is_idle() const { return state_ == EventState::Idle; }
  bool is_fault() const {
    return state_ == EventState::FaultStuck || state_ == EventState::FaultTimeout;
  }
  // Completed runs, early-close warnings, and the learned run time (a running mean, ms).
  uint32_t runs() const { return runs_; }
  uint32_t early_warnings() const { return early_; }
  uint32_t learned_run_ms() const { return learned_ms_; }

 private:
  EventMotorConfig cfg_;
  EventState state_ = EventState::Idle;
  uint32_t t0_ = 0, t_state_ = 0;
  bool home_seen_ = false;
  uint32_t runs_ = 0, early_ = 0, learned_ms_ = 0;
};

}  // namespace horloge
