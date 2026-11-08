// The forward-only follower (docs/firmware-design.md §6.2).
//
// Each axis follows its target: it never reverses, it waits while ahead, it takes a single
// µstep at once in normal running, and it makes a trapezoidal move (accelerate, cruise, decelerate)
// when the error is large: catch-up, a summer-time change, homing. The motion task calls step()
// every millisecond; the result is the number of µsteps the step ISR issues in that tick.
#pragma once
#include <cstdint>

namespace horloge {

struct FollowerConfig {
  int32_t v_max = 3200;     // µsteps/s: catch-up speed, 60 rpm (architecture §8)
  int32_t a_max = 6400;     // µsteps/s²: [E] reaches v_max in 0.5 s; set on the rig
  int32_t v_start = 400;    // µsteps/s: a start speed below the motor's pull-in rate [E]
};

struct FollowerState {
  int64_t position = 0;  // µsteps commanded so far
  int32_t v = 0;         // µsteps/s
  int64_t acc = 0;       // fractional µsteps, in µstep·ms (1000 = one µstep)
};

// Advance one tick of `dt_ms`. Returns the µsteps to issue (never more than the error).
int32_t follower_step(FollowerState& s, int64_t target, const FollowerConfig& cfg,
                      int32_t dt_ms = 1);

}  // namespace horloge
