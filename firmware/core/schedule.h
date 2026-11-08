// When the shows are due, and whether they are silenced (docs/firmware-design.md §7.3, §8.3).
//
// Shows follow legal time (D14): the quarters at :15, :30, :45 and :00 of CET/CEST, Death's count
// is the legal hour, the noon show at 12:00. Legal offsets are whole hours, so every UTC quarter
// is a legal quarter: in spring the 02:xx shows do not exist, in autumn they run twice.
#pragma once
#include <cstdint>

#include "summer_time.h"

namespace horloge {

struct Quarter {
  int64_t unix_s = 0;           // the instant, UTC
  uint8_t n = 0;                // 1..4: the pairs struck (4 on the hour)
  uint8_t hour12 = 0;           // Death's count on the hour (1..12); 0 otherwise
  bool noon = false;            // 12:00 legal time
  uint16_t legal_minute = 0;    // minute of the legal day, 0..1439
};

// The first quarter at or after `unix_s`.
Quarter quarter_at_or_after(int64_t unix_s, const SummerTimeConfig& st);

// ---- quiet hours (D10; F6: 22:00-07:00, E2 silent) ----

// Since PR #21 E2's racks are released by the walk train, so the ages, the genie and Death are
// silenced together: one class.
enum class ShowClass : uint8_t { E2 = 0, Hourglass = 1, Noon = 2 };
constexpr int kShowClasses = 3;

struct QuietConfig {
  uint16_t start_minute = 22 * 60;   // legal time
  uint16_t end_minute = 7 * 60;      // start == end: no window
  bool silences[kShowClasses] = {true, false, true};  // F6: E2 silent; the hourglass is silent anyway
  int64_t quiet_now_until_unix_s = 0;                 // Home Assistant's "quiet now"
};

bool in_quiet_window(uint16_t legal_minute, const QuietConfig& q);
bool is_quiet(ShowClass c, uint16_t legal_minute, int64_t unix_s, const QuietConfig& q);

// ---- the E2 ring (docs/firmware-design.md §7.5) ----

// Ages 0..3: child, youth, man, old man. Quarter n is struck by age n-1, and after it the age for
// the next quarter waits at the right doorway.
constexpr uint8_t age_for_quarter(uint8_t n) { return static_cast<uint8_t>((n + 3) % 4); }
constexpr uint8_t age_waiting_after(uint8_t n) { return static_cast<uint8_t>(n % 4); }
// Program turns the resync must run (two walk releases each) to bring `due` to the doorway.
constexpr uint8_t resync_turns(uint8_t waiting, uint8_t due) {
  return static_cast<uint8_t>((due + 4 - waiting) % 4);
}

}  // namespace horloge
