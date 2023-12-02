#pragma once
#include <stdint.h>
#include <SimpleSerialProtocol.h>
#include "arduino_error_blinker.h"

#ifdef NUM_MOTORS
const int NumMotors = NUM_MOTORS;
#else
const int NumMotors = 7;
#endif


class ArdJetInterface {
  public:
  ArdJetInterface(SimpleSerialProtocol sp, byte led_num) : ssp(sp), blinker(led_num) {}
  
  void awaitConnection(char InitChar) {
    while (true) {
      char rec = ssp.readChar();
      if (rec == InitChar) {
        blinker.set(LOW);
        break;
      } else {
        blinker.blink_connecting();
        ssp.writeChar(InitChar);
      }
    }
  }

  bool recv_motor_values(uint16_t motor_vals[NumMotors]) {
    err = 0;
    char message;
    message = ssp.readChar();
    
    // Check for error in reading
    if (message != 'M' || err) {
      // If reading failed or start character is wrong, reset err_num and return.
      err = 0;
      putback = message;
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

    ssp.readEot();
    if (err) { err = 0; return false; }

    return true;
  }
  
  void fastblink() {
      for (int i = 0; i < 10; i++) {
      digitalWrite(LED_BUILTIN, HIGH);
      delay(80);
      digitalWrite(LED_BUILTIN, LOW);
      delay(80);
    }
  }

  void onError(uint8_t err_num) {
    switch (err_num)
    {
    case ERROR_WAIT_FOR_BYTE_TIMEOUT:
      blinker.blink_timeout();
      err = 1;
      break;
    case ERROR_IS_DEAD:
      break;
    default:
      blinker.blink_generic();
      break;
    }
  }

  void continue_blinking() {
    blinker.continue_blinking();
  }

  uint8_t check_error() {
    return err;
  }

  char check_last_char() {
    return putback;
  }

  public:
  ErrorBlinker blinker;

  private:
  char putback;
  uint8_t err; 
  SimpleSerialProtocol ssp;
};
