#include "persist.h"

namespace horloge {

uint32_t crc32(const uint8_t* data, size_t n) {
  uint32_t c = 0xFFFFFFFFu;
  for (size_t i = 0; i < n; ++i) {
    c ^= data[i];
    for (int k = 0; k < 8; ++k) c = (c >> 1) ^ (0xEDB88320u & (0u - (c & 1u)));
  }
  return ~c;
}

namespace {
struct Writer {
  uint8_t* p;
  void u(uint64_t v, int bytes) {
    for (int i = 0; i < bytes; ++i) *p++ = static_cast<uint8_t>(v >> (8 * i));
  }
};
struct Reader {
  const uint8_t* p;
  uint64_t u(int bytes) {
    uint64_t v = 0;
    for (int i = 0; i < bytes; ++i) v |= static_cast<uint64_t>(*p++) << (8 * i);
    return v;
  }
};
}  // namespace

void encode_record(const PersistRecord& r, uint8_t out[kRecordBytes]) {
  Writer w{out};
  w.u(kRecordVersion, 1);
  w.u(r.seq, 4);
  for (int i = 0; i < kAxes; ++i) w.u(static_cast<uint64_t>(r.position[i]), 8);
  for (int i = 0; i < kAxes; ++i) w.u(static_cast<uint64_t>(r.p_k[i]), 8);
  for (int i = 0; i < kAxes; ++i) w.u(r.mscnt[i], 2);
  w.u(static_cast<uint32_t>(r.j), 4);
  w.u(r.walk_phase, 1);
  w.u(r.e6_divisions, 1);
  w.u(r.ring_age, 1);
  w.u(r.flags, 1);
  w.u(r.faults, 4);
  w.u(crc32(out, kRecordBytes - 4), 4);
}

bool decode_record(const uint8_t in[kRecordBytes], PersistRecord& r) {
  Reader rd{in};
  if (rd.u(1) != kRecordVersion) return false;
  const uint32_t want = static_cast<uint32_t>(Reader{in + kRecordBytes - 4}.u(4));
  if (crc32(in, kRecordBytes - 4) != want) return false;
  r.seq = static_cast<uint32_t>(rd.u(4));
  for (int i = 0; i < kAxes; ++i) r.position[i] = static_cast<int64_t>(rd.u(8));
  for (int i = 0; i < kAxes; ++i) r.p_k[i] = static_cast<int64_t>(rd.u(8));
  for (int i = 0; i < kAxes; ++i) r.mscnt[i] = static_cast<uint16_t>(rd.u(2));
  r.j = static_cast<int32_t>(static_cast<uint32_t>(rd.u(4)));
  r.walk_phase = static_cast<uint8_t>(rd.u(1));
  r.e6_divisions = static_cast<uint8_t>(rd.u(1));
  r.ring_age = static_cast<uint8_t>(rd.u(1));
  r.flags = static_cast<uint8_t>(rd.u(1));
  r.faults = static_cast<uint32_t>(rd.u(4));
  return true;
}

bool newest_record(const uint8_t a[kRecordBytes], const uint8_t b[kRecordBytes],
                   PersistRecord& r) {
  PersistRecord ra, rb;
  const bool va = decode_record(a, ra), vb = decode_record(b, rb);
  if (!va && !vb) return false;
  // Sequence numbers compared with wrap-around: b is newer if (b − a) is a small positive step.
  if (va && vb) r = (static_cast<int32_t>(rb.seq - ra.seq) > 0) ? rb : ra;
  else r = va ? ra : rb;
  return true;
}

int next_slot(const uint8_t a[kRecordBytes], const uint8_t b[kRecordBytes]) {
  PersistRecord ra, rb;
  const bool va = decode_record(a, ra), vb = decode_record(b, rb);
  if (!va) return 0;
  if (!vb) return 1;
  return (static_cast<int32_t>(rb.seq - ra.seq) > 0) ? 0 : 1;  // overwrite the older
}

}  // namespace horloge
