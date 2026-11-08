// E6, the calendar ring's nightly advance (docs/firmware-design.md §7.4; docs/m2-design.md §6).
//
// Released by the M2 index at mean midnight. Each motor turn moves the ring one division and ends
// when the home Hall fires (the "lock" of the EventMotor). Then the stop-lever opto decides:
// beam clear (the lever held back) = step again; beam blocked = rest. A night is capped at four
// divisions: a fifth request is a fault. The opto blocks at rest, so a dead opto stops after one.
#pragma once
#include <cstdint>

#include "event_motor.h"

namespace horloge {

enum class E6State : uint8_t { Idle, Stepping, Done, FaultCap, FaultMotor };

class E6Night {
 public:
  explicit E6Night(const EventMotorConfig& motor_cfg = {}) : motor_(motor_cfg) {}

  bool start(uint32_t now_ms);
  // `home_closed`: the home Hall (closed at rest). `beam_clear`: the stop-lever opto.
  MotorCmd tick(uint32_t now_ms, bool home_closed, bool beam_clear);

  E6State state() const { return state_; }
  uint8_t divisions() const { return divisions_; }
  static constexpr uint8_t kMaxDivisions = 4;

 private:
  EventMotor motor_;
  E6State state_ = E6State::Idle;
  uint8_t divisions_ = 0;
  bool running_ = false;
};

}  // namespace horloge
