#pragma once
#include <stdint.h>
#include <SimpleSerialProtocol.h>
#include "arduino_error_blinker.h"

#ifdef NUM_MOTORS
const int NumMotors = NUM_MOTORS;
#else
const int NumMotors = 7;
#endif

/**
 * @brief Implementation of the Arduino side of the Jetson-Arduino interface.
 * 
 * Contains functions to establish a connection with the Jetson, and for exchanging of data.
 * 
 */
class ArdJetInterface {
  public:
  ArdJetInterface(SimpleSerialProtocol sp, byte led_num) : ssp(sp), blinker(led_num) {}
  
  /**
   * @brief Wait for a connection handshake with the Jetson.
   * 
   * This function constantly transmits a single character while waiting for a reply of the same
   * character.
   * 
   * Upon receiving init_char on the Serial connection, connection is established and the function
   * exits.
   * 
   * @param init_char Character to listen for / transmit
   */
  void awaitConnection(char init_char) {
    while (true) {
      char rec = ssp.readChar();
      if (rec == init_char) {
        blinker.set(LOW);
        break;
      } else {
        blinker.blink_connecting();
        ssp.writeChar(init_char);
      }
    }
  }

  /**
   * @brief Listens for motor values transmission over the Serial connection.
   * 
   * An 'M' character marks the start of a motor value message. If this function reads an initial
   * character which is not 'M', it places the character received in the `putback` variable, for
   * processing by other functions.
   * 
   * If the whole message is successfully received, this function returns true. Otherwise, this
   * function returns false.
   * 
   * @param motor_vals 
   * @return true if the whole motor values message is successfully received, false if not
   */
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

  /**
   * @brief Send a pressure value over the Serial connection.
   * 
   * @param pressure 
   */
  void send_depth(float depth) {
    ssp.writeFloat(depth);

    // End pressure message
    ssp.writeEot();
  }
  
  /**
   * @brief Rapidly flash the onboard LED. For debugging.
   * 
   */
  void fastblink() {
      for (int i = 0; i < 10; i++) {
      digitalWrite(LED_BUILTIN, HIGH);
      delay(80);
      digitalWrite(LED_BUILTIN, LOW);
      delay(80);
    }
  }

  /**
   * @brief Error callback function, called if an error in the protocol (timeout while waiting, 
   * received unexpected character, etc.) is encountered.
   * 
   * Currently starts a blink sequence corresponding to the error.
   * 
   * @param err_num Error code. Check SimpleSerialProtocol documentation for more details.
   */
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

  /**
   * @brief Sustains the current error blinking, if one is occurring. Refer to the
   * arduino_error_blinker code documentation for more details.
   * 
   */
  void continue_blinking() {
    blinker.continue_blinking();
  }

  /**
   * @brief Check the current error code.
   * 
   * @return uint8_t - current error code
   */
  uint8_t check_error() {
    return err;
  }

  /**
   * @brief Check the putback char. This variable is set when an unexpected character is received
   * by the recv_motor_values() function.
   * 
   * @return char - putback char
   */
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
