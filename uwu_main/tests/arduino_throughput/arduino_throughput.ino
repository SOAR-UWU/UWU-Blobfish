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

#define NUM_MOTORS 7

uint64_t n_received = 0;

uint8_t err = 0;


void onError(uint8_t err_num);
SimpleSerialProtocol ssp{Serial, BaudRate, CharTimeout, onError, 'a', 'z'};
ArdJetInterface aji {ssp, LED_BUILTIN};

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
  ssp.init();
  aji.awaitConnection(InitChar);
}

void loop() {
  uint16_t motor_values[7];
  bool received = aji.recv_motor_values(motor_values);
  if (received) {
    n_received++;
  } else if (aji.check_last_char() == 'E') {
    // Test complete, send back stats
    ssp.writeChar('M');
    ssp.writeUnsignedInt64(n_received);
  }

  aji.blinker.continue_blinking();
}

void onError(uint8_t err_num) {
  aji.onError(err_num);
}