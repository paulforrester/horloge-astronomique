// EU summer time, as a firmware function (docs/firmware-design.md §8.2).
//
// Rule: summer time starts and ends at 01:00 GMT (UTC) on the last Sunday of March and of October
// [S: Directive 2000/84/EC, Arts. 2-3, https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32000L0084].
//
// J counts the hours the legal-time modules (M1b, E2 state) have been advanced since the law's
// epoch: +1 at each spring change and +23 at each autumn change (D14: forward only; +23 h is −1 h
// on the 12 h and 24 h trains). If the EU stops changing the clocks, `frozen_after_unix_s` stops J.
#pragma once
#include <cstdint>

namespace horloge {

struct SummerTimeConfig {
  bool changes_enabled = true;
  // No change at or after this instant (Unix s). INT64_MAX: never frozen.
  int64_t frozen_after_unix_s = INT64_MAX;
};

// The UTC instant (Unix s) of the spring (true) or autumn (false) change in `year`.
int64_t eu_change_unix_s(int32_t year, bool spring);

// True if `unix_s` is in summer time (CEST) under the config.
bool is_summer_time(int64_t unix_s, const SummerTimeConfig& cfg);

// Legal-time offset from UTC in seconds: 3600 (CET) or 7200 (CEST).
int32_t legal_offset_s(int64_t unix_s, const SummerTimeConfig& cfg);

// J at `unix_s`: the hours added by changes since the epoch (2026-01-01), changes at exactly
// `unix_s` included.
int32_t summer_time_j(int64_t unix_s, const SummerTimeConfig& cfg);

}  // namespace horloge
