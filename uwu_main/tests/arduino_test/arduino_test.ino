#include <SimpleSerialProtocol.h>
#include <stdint.h>


// Constants
// TODO read constants from a config file instead of hardcoding
const int BaudRate = 9600;
const int CharTimeout = 500;  // waittime for timeout between chars, in ms
const char InitChar = 'S'; // setup char

// Functions
void onError(uint8_t err_num);
void awaitConnection(SimpleSerialProtocol ssp, char InitChar);

void fastBlink() {
  for (int i = 0; i < 10; i++) {
    digitalWrite(LED_BUILTIN, HIGH);
    delay(100);
    digitalWrite(LED_BUILTIN, LOW);
    delay(100);
  }
}

SimpleSerialProtocol ssp{Serial, BaudRate, CharTimeout, onError, 'a', 'z'};

void setup() {
  // put your setup code here, to run once:
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
  fastBlink();

  ssp.init();
  // spam(ssp);

  awaitConnection(ssp, InitChar);
}

void loop() {
  // put your main code here, to run repeatedly:
  // uint16_t rec = ssp.readUnsignedInt16();
  // ssp.readEot();
  // char c_str[10];
  // utoa(rec, c_str, 10);
  // ssp.writeCString(c_str);
  ssp.writeChar('D');
  delay(1000);
}

void onError(uint8_t err_num) {
  fastBlink();
}

void awaitConnection(SimpleSerialProtocol ssp, char InitChar) {
  while (true) {
    char rec = ssp.readChar();
    if (rec == InitChar) {
      break;
    } else {
      ssp.writeChar(InitChar);
    }
  }
}

