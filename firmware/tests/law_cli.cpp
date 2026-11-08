// A command-line front end to the firmware's time law, so pytest can compare it with the Python
// reference in sim/timelaw.py (docs/firmware-design.md §11.6). One query per line on stdin:
//   T <mean|legal> <utc_unix_us> <j> <p_k>   → target µsteps
//   J <unix_s>                               → summer-time count
//   O <unix_s>                               → legal offset, s
//   Q <unix_s>                               → quarter: unix_s n hour12 noon legal_minute
#include <cstdio>
#include <cstring>

#include "../core/schedule.h"
#include "../core/summer_time.h"
#include "../core/time_law.h"

using namespace horloge;

int main() {
  char line[256];
  const SummerTimeConfig st;
  while (std::fgets(line, sizeof line, stdin)) {
    char op = 0, kind[16] = {};
    long long a = 0, b = 0, c = 0;
    if (std::sscanf(line, " %c", &op) != 1) continue;
    if (op == 'T' && std::sscanf(line, " T %15s %lld %lld %lld", kind, &a, &b, &c) == 4) {
      const TimeKind k = std::strcmp(kind, "mean") == 0 ? TimeKind::Mean : TimeKind::Legal;
      std::printf("%lld\n", (long long)target_usteps(k, a, static_cast<int32_t>(b), c));
    } else if (op == 'J' && std::sscanf(line, " J %lld", &a) == 1) {
      std::printf("%d\n", summer_time_j(a, st));
    } else if (op == 'O' && std::sscanf(line, " O %lld", &a) == 1) {
      std::printf("%d\n", legal_offset_s(a, st));
    } else if (op == 'Q' && std::sscanf(line, " Q %lld", &a) == 1) {
      const Quarter q = quarter_at_or_after(a, st);
      std::printf("%lld %d %d %d %d\n", (long long)q.unix_s, q.n, q.hour12, q.noon ? 1 : 0,
                  q.legal_minute);
    } else {
      std::printf("?\n");
    }
  }
  return 0;
}
