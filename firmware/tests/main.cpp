#include "harness.h"

int main() {
  int failed_cases = 0;
  for (const auto& c : th::cases()) {
    const int before = th::failures();
    c.fn();
    const bool ok = th::failures() == before;
    std::printf("%s %s\n", ok ? "ok  " : "FAIL", c.name);
    if (!ok) ++failed_cases;
  }
  std::printf("%zu cases, %d failed\n", th::cases().size(), failed_cases);
  return failed_cases ? 1 : 0;
}
