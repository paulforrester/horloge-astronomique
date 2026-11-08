#include "schedule.h"

#include "time_law.h"

namespace horloge {

Quarter quarter_at_or_after(int64_t unix_s, const SummerTimeConfig& st) {
  Quarter q;
  q.unix_s = floor_div(unix_s + 899, 900) * 900;
  const int64_t legal = q.unix_s + legal_offset_s(q.unix_s, st);
  const int64_t sod = floor_mod(legal, 86400);  // second of the legal day
  q.legal_minute = static_cast<uint16_t>(sod / 60);
  const int64_t quarter_of_hour = (sod % 3600) / 900;  // 0 on the hour
  q.n = static_cast<uint8_t>(quarter_of_hour == 0 ? 4 : quarter_of_hour);
  if (q.n == 4) {
    const int64_t h24 = sod / 3600;
    q.hour12 = static_cast<uint8_t>(h24 % 12 == 0 ? 12 : h24 % 12);
    q.noon = (h24 == 12);
  }
  return q;
}

bool in_quiet_window(uint16_t m, const QuietConfig& q) {
  if (q.start_minute == q.end_minute) return false;
  if (q.start_minute < q.end_minute) return m >= q.start_minute && m < q.end_minute;
  return m >= q.start_minute || m < q.end_minute;  // across midnight
}

bool is_quiet(ShowClass c, uint16_t legal_minute, int64_t unix_s, const QuietConfig& q) {
  if (!q.silences[static_cast<int>(c)]) return false;
  return in_quiet_window(legal_minute, q) || unix_s < q.quiet_now_until_unix_s;
}

}  // namespace horloge
