#include "e6.h"

namespace horloge {

bool E6Night::start(uint32_t now_ms) {
  if (state_ == E6State::Stepping) return false;
  divisions_ = 0;
  if (!motor_.release(now_ms)) {
    state_ = E6State::FaultMotor;
    return false;
  }
  running_ = true;
  state_ = E6State::Stepping;
  return true;
}

MotorCmd E6Night::tick(uint32_t now_ms, bool home_closed, bool beam_clear) {
  if (state_ != E6State::Stepping) return MotorCmd::Off;
  const MotorCmd cmd = motor_.tick(now_ms, home_closed);
  if (motor_.is_fault()) {
    state_ = E6State::FaultMotor;
    return MotorCmd::Brake;
  }
  if (running_ && motor_.is_idle()) {  // one division done, braked and settled
    running_ = false;
    ++divisions_;
    if (!beam_clear) {
      state_ = E6State::Done;
    } else if (divisions_ >= kMaxDivisions) {
      state_ = E6State::FaultCap;  // the lever still asks for more after four
    } else {
      motor_.release(now_ms);
      running_ = true;
      return MotorCmd::Run;
    }
  }
  return cmd;
}

}  // namespace horloge
