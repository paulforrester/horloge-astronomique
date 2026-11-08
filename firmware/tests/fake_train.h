// A fake event train for the host tests: it turns while commanded to Run and stops on Brake.
// Its lock switch opens soon after it starts and closes again `duration` ms of running later.
// Optional: brief lock closings every `lock_every` ms (a counting train's strike shaft), a home
// opto that blocks only at the end, and cue pulses at given times into the run.
#pragma once
#include <cstdint>
#include <vector>

#include "../core/event_motor.h"

struct FakeTrain {
  std::vector<uint32_t> durations;  // one per run; the last repeats
  uint32_t lock_every = 0;          // 0: no intermediate closings
  std::vector<uint32_t> cues;       // ms into the run
  bool never_moves = false;         // jammed: the lock never opens
  bool never_locks = false;         // the lock never closes again

  bool running = false;
  uint32_t run_ms = 0;
  size_t runs = 0;

  uint32_t duration() const {
    return durations.empty() ? 1000 : durations[runs < durations.size() ? runs : durations.size() - 1];
  }
  void apply(horloge::MotorCmd cmd, uint32_t dt_ms) {
    if (cmd == horloge::MotorCmd::Run && !never_moves) {
      if (!running) { running = true; run_ms = 0; }
      run_ms += dt_ms;
      if (!never_locks && run_ms >= duration()) { running = false; ++runs; run_ms = 0; }
    }
  }
  bool lock() const {
    if (!running) return true;
    if (run_ms < 30) return true;  // still in the notch for the first moment
    if (lock_every && run_ms % lock_every < 30 && run_ms + 30 < duration()) return true;
    return false;
  }
  bool home() const { return !running; }
  bool cue() const {
    if (!running) return false;
    for (uint32_t c : cues) if (run_ms >= c && run_ms < c + 200) return true;
    return false;
  }
};
