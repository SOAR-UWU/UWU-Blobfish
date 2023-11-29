#pragma once
#include <SimpleSerialProtocol.h>
#include "arduino_error_codes.h"

#ifdef NUM_MOTORS
const int NumMotors = NUM_MOTORS;
#else
const int NumMotors = 7;
#endif

extern uint8_t err; // there's probably a better way to do this. Take a look at the ssp errors if you can think of something

void awaitConnection(SimpleSerialProtocol ssp, char InitChar) {
  while (true) {
    char rec = ssp.readChar();
    if (rec == InitChar) {
      digitalWrite(LED_BUILTIN, LOW);
      break;
    } else {
      BlinkPatterns::blink_connecting();
      ssp.writeChar(InitChar);
    }
  }
}

bool recv_motor_values(SimpleSerialProtocol ssp, uint16_t motor_vals[NumMotors]) {
  err = 0;
  char message_start = ssp.readChar();
  
  // Check for error in reading
  if (message_start != 'M' || err) {
    // If reading failed or start character is wrong, reset err_num and return.
    err = 0;
    return false;
  }

  motor_vals[0] = ssp.readUnsignedInt16();
  if (err) { err = 0; return false; }
  motor_vals[1] = ssp.readUnsignedInt16();
  if (err) { err = 0; return false; }
  motor_vals[2] = ssp.readUnsignedInt16();
  if (err) { err = 0; return false; }
  motor_vals[3] = ssp.readUnsignedInt16();
  if (err) { err = 0; return false; }
  motor_vals[4] = ssp.readUnsignedInt16();
  if (err) { err = 0; return false; }
  motor_vals[5] = ssp.readUnsignedInt16();
  if (err) { err = 0; return false; }
  motor_vals[6] = ssp.readUnsignedInt16();
  if (err) { err = 0; return false; }

  return true;
}