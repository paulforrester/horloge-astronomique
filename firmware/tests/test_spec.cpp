// The generated header compiles, and agrees with the core (its static_asserts) and the module docs.
#include "../spec_gen/spec_gen.h"
#include "harness.h"

using namespace horloge;

TEST(spec_axes_and_events) {
  CHECK_EQ(spec::kAxisCount, 7);
  CHECK(spec::kAxes[1].time == TimeKind::Legal);   // M1b follows legal time (D9, D14)
  CHECK(spec::kAxes[2].time == TimeKind::Legal);   // so does E2's state arbor
  CHECK_EQ(spec::kAxes[3].reduction, 24u);         // M2: 24:1 to a daily arbor
  CHECK_EQ(spec::kSensorCount, 31);                // firmware-design §3.5, v1
  CHECK_EQ(spec::kE2WalkANominalMs, 8680u);
  CHECK_EQ(spec::kM1QuartersWindowS, 176);         // 2.94 min
}
