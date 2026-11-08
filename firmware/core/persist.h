// The FRAM state record (docs/firmware-design.md §9.4).
//
// Written each second and on every change of state, into two alternating slots. Each slot carries
// a sequence number and a CRC-32; at power-up the newer slot with a valid CRC wins, so a write
// cut by a power loss can never corrupt the state. The byte layout is fixed little-endian, so it
// does not depend on the compiler.
#pragma once
#include <cstddef>
#include <cstdint>

namespace horloge {

constexpr int kAxes = 8;  // stepper sockets (7 used by v1.5)

struct PersistRecord {
  uint32_t seq = 0;
  int64_t position[kAxes] = {};   // µsteps commanded
  int64_t p_k[kAxes] = {};        // calibration from homing (§9.2)
  uint16_t mscnt[kAxes] = {};     // TMC2209 microstep counter, for the phase restore (F4)
  int32_t j = 0;                  // the summer-time count (§6.1)
  uint8_t walk_phase = 0;         // E2 walk: 0 at rest, 1 locked for the strikes
  uint8_t e6_divisions = 0;       // E6 divisions made tonight
  uint8_t ring_age = 0;           // E2: the age waiting at the right doorway (0..3)
  uint8_t flags = 0;              // spare
  uint32_t faults = 0;            // active fault bits
};

constexpr uint8_t kRecordVersion = 1;
// version 1 + seq 4 + positions 64 + p_k 64 + mscnt 16 + j 4 + 4 bytes + faults 4 + crc 4
constexpr size_t kRecordBytes = 1 + 4 + 8 * kAxes + 8 * kAxes + 2 * kAxes + 4 + 4 + 4 + 4;

uint32_t crc32(const uint8_t* data, size_t n);  // IEEE 802.3, reflected, init and xorout ~0

void encode_record(const PersistRecord& r, uint8_t out[kRecordBytes]);
// False if the version or CRC is wrong.
bool decode_record(const uint8_t in[kRecordBytes], PersistRecord& r);

// The slot to write next (0 or 1), given which slots hold valid records.
int next_slot(const uint8_t a[kRecordBytes], const uint8_t b[kRecordBytes]);
// The newest valid record of the two slots; false if neither is valid.
bool newest_record(const uint8_t a[kRecordBytes], const uint8_t b[kRecordBytes], PersistRecord& r);

}  // namespace horloge
