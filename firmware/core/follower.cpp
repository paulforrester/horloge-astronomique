#include "follower.h"

namespace horloge {

int32_t follower_step(FollowerState& s, int64_t target, const FollowerConfig& cfg,
                      int32_t dt_ms) {
  const int64_t err = target - s.position;
  if (err <= 0) {  // ahead or on target: wait, never reverse
    s.v = 0;
    s.acc = 0;
    return 0;
  }
  if (s.v == 0) {  // starting from rest: the first µstep goes at once
    s.v = cfg.v_start;
    s.acc = 1000;
  } else {
    // Stopping distance at the current speed, v² / 2a, in µsteps (rounded up).
    const int64_t v = s.v;
    const int64_t stop = (v * v + 2LL * cfg.a_max - 1) / (2LL * cfg.a_max);
    const int64_t dv = static_cast<int64_t>(cfg.a_max) * dt_ms / 1000;
    if (err > stop + 1) {
      s.v = static_cast<int32_t>(v + dv > cfg.v_max ? cfg.v_max : v + dv);
    } else {
      s.v = static_cast<int32_t>(v - dv < cfg.v_start ? cfg.v_start : v - dv);
    }
    s.acc += static_cast<int64_t>(s.v) * dt_ms;
  }
  int64_t n = s.acc / 1000;
  if (n > err) n = err;
  s.acc -= n * 1000;
  s.position += n;
  if (s.position == target) {  // landed: the next move starts from rest
    s.v = 0;
    s.acc = 0;
  }
  return static_cast<int32_t>(n);
}

}  // namespace horloge
