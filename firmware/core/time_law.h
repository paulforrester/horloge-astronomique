// The clockwork time law (docs/firmware-design.md §6.1, architecture P1).
//
// Every module stepper turns its motor at 1 rev/h = 3200 µsteps/h, one µstep every 1.125 s.
// Its commanded position is a pure function of time:
//
//     target_k(t) = P_k + floor( (τ_k(t) − τ_ref) × 8 / 9 s )        [µsteps]
//
// τ_k is the module's own time: Strasbourg mean time for M1, M2, M3, M5, M6; a forward-only legal
// time for M1b and the E2 state arbor (UTC + 1 h + 1 h × J, J from summer_time.h).
// Integers only: no floating point, no overflow for millennia.
#pragma once
#include <cstdint>

namespace horloge {

// Strasbourg mean time = UT + 31.00 min (D2) [D: 7.7506° × 240 s/° = 1860.1 s].
constexpr int64_t kMeanTimeOffsetS = 1860;
// CET = UTC + 1 h.
constexpr int64_t kCetOffsetS = 3600;
// The law's epoch: 2026-01-01 00:00:00 UTC, as Unix seconds.
constexpr int64_t kEpochUnixS = 1767225600;

constexpr int64_t kUsPerS = 1000000;
// 3200 µsteps per 3600 s = 8 µsteps per 9 s.
constexpr int64_t kLawNum = 8;
constexpr int64_t kLawDenUs = 9 * kUsPerS;
constexpr int64_t kUstepsPerMotorRev = 3200;  // 200 full steps × 16

enum class TimeKind : uint8_t { Mean, Legal };

// floor(a / b) for b > 0, correct for negative a.
constexpr int64_t floor_div(int64_t a, int64_t b) {
  return (a >= 0) ? a / b : -((-a + b - 1) / b);
}
constexpr int64_t floor_mod(int64_t a, int64_t b) { return a - floor_div(a, b) * b; }

// µsteps for a span of module time, floor((dt_us × 8) / 9e6), without overflowing int64.
constexpr int64_t usteps_for(int64_t dt_us) {
  const int64_t q = floor_div(dt_us, kLawDenUs);
  const int64_t r = dt_us - q * kLawDenUs;  // 0 <= r < 9e6
  return q * kLawNum + (r * kLawNum) / kLawDenUs;
}

// The module's own time, in µs since the epoch. `j` is the summer-time count (legal modules only).
constexpr int64_t module_time_us(TimeKind kind, int64_t utc_unix_us, int32_t j) {
  const int64_t since_epoch = utc_unix_us - kEpochUnixS * kUsPerS;
  if (kind == TimeKind::Mean) return since_epoch + kMeanTimeOffsetS * kUsPerS;
  return since_epoch + (kCetOffsetS + 3600LL * j) * kUsPerS;
}

// Commanded position of a module stepper, in µsteps. `p_k` is its calibration (§9.2).
constexpr int64_t target_usteps(TimeKind kind, int64_t utc_unix_us, int32_t j, int64_t p_k) {
  return p_k + usteps_for(module_time_us(kind, utc_unix_us, j));
}

}  // namespace horloge
