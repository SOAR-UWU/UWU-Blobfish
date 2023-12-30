/**
 * Sketch for testing of Jetson interface functions. To compile this, link with the header files in
 * the /arduino folder in the root of this repo (e.g. with arduino-cli, using the --library option to
 * point at the /arduino folder).
*/

#include <SimpleSerialProtocol.h>
#include <stdint.h>
#include "arduino_error_blinker.h"
#include "arduino_jetson_interface.h"

// Constants
// TODO read constants from a config file instead of hardcoding
const int BaudRate = 9600;
const int CharTimeout = 10;  // waittime for timeout between chars, in ms
const char InitChar = 'S'; // setup char

uint16_t count = 0;  // number of transmissions received

#define NUM_MOTORS 7

void onError(uint8_t err_num);
SimpleSerialProtocol ssp{Serial, BaudRate, CharTimeout, onError, 'a', 'z'};
ArdJetInterface aji {ssp, LED_BUILTIN};

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
  ssp.init();
  aji.awaitConnection(InitChar);
  count = 0;
}

void loop() {
  uint16_t motor_values[7];
  bool received = aji.recv_motor_values(motor_values);
  if (received) {
    ssp.writeChar('M');
    for (auto val : motor_values) {
      ssp.writeUnsignedInt16(val);
    }
    count++;
  } else if (aji.check_last_char() == 'E') {  // multiple transmissions test
    ssp.writeChar('M');
    for (auto val : motor_values) {
      ssp.writeUnsignedInt16(val);
    }
    ssp.writeEot();
    ssp.writeUnsignedInt16(count);
    ssp.writeEot();
  }

  aji.continue_blinking();
}

void onError(uint8_t err_num) {
  aji.onError(err_num);
}


