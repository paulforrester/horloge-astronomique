// A minimal unit-test harness, so the host tests need nothing downloaded (docs/firmware-design.md §12.1).
#pragma once
#include <cstdio>
#include <functional>
#include <string>
#include <vector>

namespace th {

struct Case {
  const char* name;
  std::function<void()> fn;
};
inline std::vector<Case>& cases() {
  static std::vector<Case> v;
  return v;
}
inline int& failures() {
  static int f = 0;
  return f;
}
struct Reg {
  Reg(const char* n, std::function<void()> f) { cases().push_back({n, std::move(f)}); }
};

}  // namespace th

#define TH_CAT2(a, b) a##b
#define TH_CAT(a, b) TH_CAT2(a, b)
#define TEST(name)                                              \
  static void name();                                           \
  static th::Reg TH_CAT(reg_, name)(#name, name);               \
  static void name()

#define CHECK(cond)                                                              \
  do {                                                                           \
    if (!(cond)) {                                                               \
      std::printf("  FAIL %s:%d: %s\n", __FILE__, __LINE__, #cond);              \
      ++th::failures();                                                          \
    }                                                                            \
  } while (0)

#define CHECK_EQ(a, b)                                                           \
  do {                                                                           \
    const auto va_ = (a);                                                        \
    const auto vb_ = (b);                                                        \
    if (!(va_ == vb_)) {                                                         \
      std::printf("  FAIL %s:%d: %s == %s (%lld vs %lld)\n", __FILE__, __LINE__, \
                  #a, #b, (long long)va_, (long long)vb_);                       \
      ++th::failures();                                                          \
    }                                                                            \
  } while (0)
