#include "event_motor.h"

namespace horloge {

bool EventMotor::release(uint32_t now_ms) {
  if (state_ != EventState::Idle) return false;
  state_ = EventState::Leaving;
  t0_ = t_state_ = now_ms;
  home_seen_ = false;
  return true;
}

MotorCmd EventMotor::tick(uint32_t now_ms, bool lock_closed, bool home_blocked) {
  const uint32_t in_state = now_ms - t_state_;
  switch (state_) {
    case EventState::Idle:
      return MotorCmd::Off;
    case EventState::FaultStuck:
    case EventState::FaultTimeout:
      return MotorCmd::Brake;
    case EventState::Leaving:
      if (!lock_closed) {
        state_ = EventState::Running;
        t_state_ = now_ms;
        return MotorCmd::Run;
      }
      if (in_state > cfg_.t_leave_ms) {
        state_ = EventState::FaultStuck;
        return MotorCmd::Brake;
      }
      return MotorCmd::Run;
    case EventState::Running: {
      if (cfg_.uses_home && home_blocked) home_seen_ = true;
      const bool done = lock_closed && (!cfg_.uses_home || home_seen_);
      if (done) {
        const uint32_t run = now_ms - t0_;
        if (run < cfg_.t_run_min_ms) ++early_;
        learned_ms_ = (runs_ == 0) ? run : (learned_ms_ * 3 + run) / 4;  // mean, weight 1/4
        ++runs_;
        state_ = EventState::Braking;
        t_state_ = now_ms;
        return MotorCmd::Brake;
      }
      if (now_ms - t0_ > cfg_.t_run_max_ms) {
        state_ = EventState::FaultTimeout;
        return MotorCmd::Brake;
      }
      return MotorCmd::Run;
    }
    case EventState::Braking:
      if (in_state >= cfg_.t_brake_ms) {
        state_ = EventState::Idle;
        return MotorCmd::Off;
      }
      return MotorCmd::Brake;
  }
  return MotorCmd::Off;
}

}  // namespace horloge
