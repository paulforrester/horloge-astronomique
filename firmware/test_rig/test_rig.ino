// Test rig firmware (Phase 2 step 3): one TMC2209 stepper turning the minute arbor at 1 rev/h.
// UNTESTED: written before the hardware exists. Arduino IDE, board "ESP32S3 Dev Module",
// library "TMCStepper" (teemuatlut). Wiring and procedure: docs/test-rig.md.
//
// Time base for the rig: the ESP32's crystal (about ±20 ppm, i.e. ±1.7 s per day [E]). The clock
// proper adds the RTC and NTP (architecture §9); the rig only has to prove the mechanics.

#include <TMCStepper.h>

// ---- pins (ESP32-S3-DevKitC-1) ----
const int PIN_STEP = 4, PIN_DIR = 5, PIN_EN = 6;
const int PIN_UART_TX = 17, PIN_UART_RX = 18;     // TMC2209 PDN_UART: TX through 1 kΩ to the RX line
const int PIN_HALL_INDEX = 7;                     // minute arbor, once per hour (DRV5032, open drain)
const int PIN_HALL_WITNESS = 8;                   // 24 h arbor, once per day

// ---- motion: 200 full steps x 16 microsteps = 3200 µsteps per revolution, 1 rev per hour ----
const uint32_t USTEPS_PER_REV = 200UL * 16UL;
const uint32_t US_PER_USTEP = 3600UL * 1000000UL / USTEPS_PER_REV;   // 1 125 000 µs
const uint16_t RUN_CURRENT_MA = 500;                                   // spec/clock.yaml motor.run_current_a
const float R_SENSE = 0.11f;                                           // typical TMC2209 stepstick [Sn]

HardwareSerial& TMCSerial = Serial1;
TMC2209Stepper driver(&TMCSerial, R_SENSE, 0b00);

volatile uint32_t isr_index_count = 0, isr_witness_count = 0;
uint64_t usteps = 0, next_step_us = 0;
uint64_t last_index_usteps = 0;

void IRAM_ATTR onIndex() { isr_index_count++; }
void IRAM_ATTR onWitness() { isr_witness_count++; }

void setup() {
  Serial.begin(115200);
  pinMode(PIN_STEP, OUTPUT); pinMode(PIN_DIR, OUTPUT); pinMode(PIN_EN, OUTPUT);
  digitalWrite(PIN_DIR, LOW);            // forward only (CLAUDE.md rule 3); flip if the hands run backwards
  digitalWrite(PIN_EN, LOW);
  TMCSerial.begin(115200, SERIAL_8N1, PIN_UART_RX, PIN_UART_TX);
  driver.begin();
  driver.toff(4);
  driver.rms_current(RUN_CURRENT_MA);
  driver.microsteps(16);
  driver.en_spreadCycle(false);          // StealthChop: quiet
  driver.pwm_autoscale(true);
  pinMode(PIN_HALL_INDEX, INPUT_PULLUP);
  pinMode(PIN_HALL_WITNESS, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PIN_HALL_INDEX), onIndex, FALLING);
  attachInterrupt(digitalPinToInterrupt(PIN_HALL_WITNESS), onWitness, FALLING);
  next_step_us = esp_timer_get_time();
  Serial.printf("test rig: %lu us per microstep, driver version 0x%02x\n", (unsigned long)US_PER_USTEP, driver.version());
}

void loop() {
  uint64_t now = esp_timer_get_time();
  if ((int64_t)(now - next_step_us) >= 0) {   // one microstep on schedule; never accumulates drift
    digitalWrite(PIN_STEP, HIGH); delayMicroseconds(4); digitalWrite(PIN_STEP, LOW);
    usteps++;
    next_step_us += US_PER_USTEP;
  }
  static uint32_t seen_index = 0, seen_witness = 0;
  if (isr_index_count != seen_index) {         // index: expect exactly 3200 µsteps between passes
    seen_index = isr_index_count;
    Serial.printf("index %lu: %llu usteps since last (expect %lu)\n", (unsigned long)seen_index,
                  usteps - last_index_usteps, (unsigned long)USTEPS_PER_REV);
    last_index_usteps = usteps;
  }
  if (isr_witness_count != seen_witness) {     // witness: once per day, log the step count
    seen_witness = isr_witness_count;
    Serial.printf("witness %lu at %llu usteps\n", (unsigned long)seen_witness, usteps);
  }
}
