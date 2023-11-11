#include <SimpleSerialProtocol.h>
#include <stdint.h>


// Constants
// TODO read constants from a config file instead of hardcoding
const int BaudRate = 9600;
const int CharTimeout = 500;  // waittime for timeout between chars, in ms

// Functions
void onError(uint8_t err_num);

SimpleSerialProtocol ssp{Serial, BaudRate, CharTimeout, onError, 'a', 'z'};

void setup() {
  // put your setup code here, to run once:
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);

  ssp.init();

}

void loop() {
  // put your main code here, to run repeatedly:
  uint16_t rec = ssp.readUnsignedInt16();
  ssp.readEot();
  char c_str[10];
  utoa(rec, c_str, 10);
  ssp.writeCString(c_str);
}

void onError(uint8_t err_num) {
  for (int i = 0; i < 10; i++) {
    digitalWrite(LED_BUILTIN, HIGH);
    delay(100);
    digitalWrite(LED_BUILTIN, LOW);
  }
}

