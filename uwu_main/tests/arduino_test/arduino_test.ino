#include <SimpleSerialProtocol.h>
#include <stdint.h>
#include "arduino_error_codes.h"
#include "arduino_jetson_interface.h"


// Constants
// TODO read constants from a config file instead of hardcoding
const int BaudRate = 9600;
const int CharTimeout = 500;  // waittime for timeout between chars, in ms
const char InitChar = 'S'; // setup char

#define NUM_MOTORS 7

uint8_t err = 0;

// Functions
void onError(uint8_t err_num);
void awaitConnection(SimpleSerialProtocol ssp, char InitChar);

SimpleSerialProtocol ssp{Serial, BaudRate, CharTimeout, onError, 'a', 'z'};

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
  ssp.init();
  awaitConnection(ssp, InitChar);
}

void loop() {
  uint16_t motor_values[7];
  bool received = recv_motor_values(ssp, motor_values);
  if (received) {
    ssp.writeChar('M');
    for (auto val : motor_values) {
      ssp.writeUnsignedInt16(val);
    }
  }
}

void onError(uint8_t err_num) {
  switch (err_num)
  {
  case ERROR_WAIT_FOR_BYTE_TIMEOUT:
    BlinkPatterns::blink_timeout();   
    err = 1;
    break;
  default:
    BlinkPatterns::blink_error();
    break;
  }
}


