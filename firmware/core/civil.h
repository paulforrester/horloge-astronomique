// Gregorian calendar arithmetic on days since 1970-01-01, with no C library time zone.
// Algorithms after H. Hinnant, "chrono-Compatible Low-Level Date Algorithms"
// (https://howardhinnant.github.io/date_algorithms.html), public domain.
#pragma once
#include <cstdint>

namespace horloge {

struct CivilDate {
  int32_t year;
  uint8_t month;  // 1..12
  uint8_t day;    // 1..31
};

constexpr int64_t days_from_civil(int32_t y, unsigned m, unsigned d) {
  y -= m <= 2;
  const int64_t era = (y >= 0 ? y : y - 399) / 400;
  const unsigned yoe = static_cast<unsigned>(y - era * 400);
  const unsigned doy = (153 * (m + (m > 2 ? -3 : 9)) + 2) / 5 + d - 1;
  const unsigned doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
  return era * 146097 + static_cast<int64_t>(doe) - 719468;
}

constexpr CivilDate civil_from_days(int64_t z) {
  z += 719468;
  const int64_t era = (z >= 0 ? z : z - 146096) / 146097;
  const unsigned doe = static_cast<unsigned>(z - era * 146097);
  const unsigned yoe = (doe - doe / 1460 + doe / 36524 - doe / 146096) / 365;
  const int64_t y = static_cast<int64_t>(yoe) + era * 400;
  const unsigned doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
  const unsigned mp = (5 * doy + 2) / 153;
  const unsigned d = doy - (153 * mp + 2) / 5 + 1;
  const unsigned m = mp < 10 ? mp + 3 : mp - 9;
  return CivilDate{static_cast<int32_t>(y + (m <= 2)), static_cast<uint8_t>(m),
                   static_cast<uint8_t>(d)};
}

// 0 = Sunday … 6 = Saturday.
constexpr unsigned weekday_from_days(int64_t z) {
  return static_cast<unsigned>(z >= -4 ? (z + 4) % 7 : (z + 5) % 7 + 6);
}

constexpr unsigned last_day_of_month(int32_t y, unsigned m) {
  constexpr unsigned kDays[12] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
  const bool leap = (y % 4 == 0 && y % 100 != 0) || y % 400 == 0;
  return (m == 2 && leap) ? 29 : kDays[m - 1];
}

}  // namespace horloge
