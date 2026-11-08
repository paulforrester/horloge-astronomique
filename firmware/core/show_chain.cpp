#include "show_chain.h"

namespace horloge {

void ShowChain::begin(const ChainPlan& plan, int64_t t_ms) {
  *this = ShowChain{};
  plan_ = plan;
  t_ms_ = t_ms;
  active_ = true;
  walk_start_ms_ = t_ms - plan.walk_lead_ms;
}

bool ShowChain::release(Motor m, int64_t now_ms, EventMotor* motors) {
  started_[m] = true;
  if (order_len_ < sizeof(order_) / sizeof(order_[0])) order_[order_len_++] = m;
  if (!motors[m].release(static_cast<uint32_t>(now_ms))) {
    faults_ |= kMotorFault;  // faulted or still busy: skipped, counts as done
    return false;
  }
  return true;
}

void ShowChain::tick(int64_t now_ms, const ChainInputs& in, EventMotor* motors, MotorCmd* cmds) {
  for (int m = 0; m < kChainMotors; ++m) {
    cmds[m] = motors[m].tick(static_cast<uint32_t>(now_ms), in.lock[m], in.home[m]);
    if (motors[m].is_fault()) faults_ |= kMotorFault;
  }
  if (!active_) return;
  const Quarter& q = plan_.q;
  const bool on_hour = (q.n == 4);

  // 1. The walk out, `lead` before the quarter, if the quarter flag is up.
  if (plan_.e2 && !started_[kWalk] && now_ms >= walk_start_ms_) {
    if (in.win_quarter) {
      release(kWalk, now_ms, motors);
      walk_runs_ = 1;
    } else {
      faults_ |= kWindowQuarter;
      plan_.e2 = false;  // skip the ages and Death; the hourglass and noon fall back to T
    }
  }
  // 2. The quarter train at T, once the walk has locked for the strikes.
  if (plan_.e2 && walk_runs_ == 1 && settled(motors[kWalk]) && !started_[kQuarters] &&
      now_ms >= t_ms_) {
    release(kQuarters, now_ms, motors);
  }
  // 3. One genie stroke per E2 cue while the quarters run.
  const bool cue2_rise = in.cue_e2 && !prev_cue_e2_;
  prev_cue_e2_ = in.cue_e2;
  if (cue2_rise && started_[kQuarters] && !settled(motors[kQuarters])) {
    if (motors[kBell].release(static_cast<uint32_t>(now_ms))) {
      ++bell_strokes_;
      if (order_len_ < 16) order_[order_len_++] = kBell;
    } else {
      faults_ |= kCueMissed;
    }
  }
  // 4. Quarters done: the walk on; on the hour, the hourglass "au dernier coup des quatre quarts".
  const bool quarters_done = started_[kQuarters] && settled(motors[kQuarters]);
  if (plan_.e2 && quarters_done && walk_runs_ == 1) {
    if (on_hour && plan_.hourglass && !started_[kHourglass]) {
      if (in.win_hour) release(kHourglass, now_ms, motors);
      else { faults_ |= kWindowHour; started_[kHourglass] = true; }
    }
    if (motors[kWalk].release(static_cast<uint32_t>(now_ms))) {
      if (order_len_ < 16) order_[order_len_++] = kWalk;
    } else {
      faults_ |= kMotorFault;
    }
    walk_runs_ = 2;
  }
  // E2 silent: the hourglass at T on the hour.
  if (!plan_.e2 && on_hour && plan_.hourglass && !started_[kHourglass] && now_ms >= t_ms_) {
    if (in.win_hour) release(kHourglass, now_ms, motors);
    else { faults_ |= kWindowHour; started_[kHourglass] = true; }
  }
  // 5. Death, once the walk has locked and the hourglass has turned.
  const bool walk_done = walk_runs_ == 2 && settled(motors[kWalk]);
  const bool glass_done = !plan_.hourglass || (started_[kHourglass] && settled(motors[kHourglass]));
  if (plan_.e2 && on_hour && walk_done && glass_done && !started_[kHours]) {
    if (in.win_hour) release(kHours, now_ms, motors);
    else { faults_ |= kWindowHour; started_[kHours] = true; }
  }
  // 6. Noon: the procession once Death has locked (or at T if E2 is silent).
  const bool hours_done = started_[kHours] && settled(motors[kHours]);
  if (q.noon && plan_.noon_show && !started_[kProcession] &&
      ((plan_.e2 && hours_done) || (!plan_.e2 && now_ms >= t_ms_))) {
    if (in.win_noon) release(kProcession, now_ms, motors);
    else { faults_ |= kWindowNoon; started_[kProcession] = true; }
  }
  // 7. One crow per E3 cue while the procession runs.
  const bool cue3_rise = in.cue_e3 && !prev_cue_e3_;
  prev_cue_e3_ = in.cue_e3;
  if (cue3_rise && started_[kProcession] && !settled(motors[kProcession])) {
    if (motors[kRooster].release(static_cast<uint32_t>(now_ms))) {
      ++crows_;
      if (order_len_ < 16) order_[order_len_++] = kRooster;
    } else {
      faults_ |= kCueMissed;
    }
  }
  // Finished when every step that is due has run and every motor has settled.
  bool pending = false;
  if (plan_.e2 && (walk_runs_ < 2 || !started_[kQuarters])) pending = true;
  if (plan_.e2 && on_hour && !started_[kHours]) pending = true;
  if (on_hour && plan_.hourglass && !started_[kHourglass]) pending = true;
  if (q.noon && plan_.noon_show && !started_[kProcession]) pending = true;
  for (int m = 0; m < kChainMotors; ++m)
    if (!motors[m].is_idle() && !motors[m].is_fault()) pending = true;
  if (!pending && now_ms >= t_ms_) active_ = false;
}

}  // namespace horloge
