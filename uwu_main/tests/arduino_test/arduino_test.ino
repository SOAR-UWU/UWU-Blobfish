#include <SimpleSerialProtocol.h>
#include <stdint.h>
#include "arduino_error_codes.h"


// Constants
// TODO read constants from a config file instead of hardcoding
const int BaudRate = 9600;
const int CharTimeout = 500;  // waittime for timeout between chars, in ms
const char InitChar = 'S'; // setup char

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

void loop() {}

void onError(uint8_t err_num) {
  BlinkPatterns::blink_error();
}

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

