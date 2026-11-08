#include "summer_time.h"

#include "civil.h"
#include "time_law.h"

namespace horloge {

int64_t eu_change_unix_s(int32_t year, bool spring) {
  const unsigned month = spring ? 3 : 10;
  const int64_t last = days_from_civil(year, month, 31);  // March and October both have 31 days
  const int64_t sunday = last - weekday_from_days(last);   // back to the last Sunday
  return sunday * 86400 + 3600;                            // 01:00 UTC
}

static bool counts(int64_t change_s, const SummerTimeConfig& cfg) {
  return cfg.changes_enabled && change_s < cfg.frozen_after_unix_s;
}

bool is_summer_time(int64_t unix_s, const SummerTimeConfig& cfg) {
  if (!cfg.changes_enabled) return false;
  // After a freeze the clock keeps the state it had just before it.
  if (unix_s >= cfg.frozen_after_unix_s) unix_s = cfg.frozen_after_unix_s - 1;
  const int32_t year = civil_from_days(floor_div(unix_s, 86400)).year;
  return eu_change_unix_s(year, true) <= unix_s && unix_s < eu_change_unix_s(year, false);
}

int32_t legal_offset_s(int64_t unix_s, const SummerTimeConfig& cfg) {
  return is_summer_time(unix_s, cfg) ? 7200 : 3600;
}

int32_t summer_time_j(int64_t unix_s, const SummerTimeConfig& cfg) {
  if (!cfg.changes_enabled) return 0;
  const int32_t last_year = civil_from_days(floor_div(unix_s, 86400)).year;
  int32_t j = 0;
  for (int32_t y = 2026; y <= last_year; ++y) {
    const int64_t s = eu_change_unix_s(y, true), a = eu_change_unix_s(y, false);
    if (s <= unix_s && counts(s, cfg)) j += 1;
    if (a <= unix_s && counts(a, cfg)) j += 23;
  }
  return j;
}

}  // namespace horloge
