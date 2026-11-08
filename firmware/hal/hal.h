// The interfaces the firmware core is driven through (docs/firmware-design.md §5.1).
//
// The core never touches hardware. On the ESP32-S3, firmware/board/ implements these with the
// TMC2209s, PCA9685, MCP23017s, RV-3028-C7 and FRAM. On the host, the tests use fakes.
#pragma once
#include <cstddef>
#include <cstdint>

#include "../core/event_motor.h"

namespace horloge {

class Clock {
 public:
  virtual ~Clock() = default;
  virtual int64_t utc_unix_us() = 0;   // disciplined UTC (§8.1)
  virtual uint32_t millis() = 0;       // monotonic
};

class Steppers {
 public:
  virtual ~Steppers() = default;
  virtual void issue(int axis, int32_t usteps) = 0;  // forward only
  virtual uint16_t mscnt(int axis) = 0;              // TMC2209 MSCNT (0..1023)
  virtual bool open_load(int axis) = 0;              // module unplugged (§3.3)
  virtual void enable_all(bool on) = 0;              // the shared EN line
};

class Motors {
 public:
  virtual ~Motors() = default;
  virtual void command(int motor, MotorCmd cmd) = 0;
  virtual void kill() = 0;  // PCA9685 OE: brake everything at once (§3.4)
};

class Inputs {
 public:
  virtual ~Inputs() = default;
  virtual bool read(int input) = 0;  // debounced (§7.2)
};

class Store {
 public:
  virtual ~Store() = default;
  virtual bool read(size_t addr, uint8_t* buf, size_t n) = 0;
  virtual bool write(size_t addr, const uint8_t* buf, size_t n) = 0;
};

}  // namespace horloge
