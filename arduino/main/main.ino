#include <Servo.h>
#include "arduino_jetson_interface.h"
#include <Wire.h>
#include "MS5837.h"

MS5837 sensor;

// Just to make it easier to see which pins, doesn't take up too much space
const byte motor_1 = 2;
const byte motor_2 = 3;
const byte motor_3 = 5;
const byte motor_4 = 6;
const byte motor_5 = 9;
const byte motor_6 = 10;
const byte motor_7 = 11;

const byte motor_pins[7] {motor_1,motor_2,motor_3,motor_4,motor_5,motor_6,motor_7};
Servo motors[7];

// Serial protocol constants
const int BaudRate = 19200;
const int CharTimeout = 10;  // waittime for timeout between chars, in ms
const char InitChar = 'S'; // setup char

#define NUM_MOTORS 7

void onError(uint8_t err_num);
SimpleSerialProtocol ssp{Serial, BaudRate, CharTimeout, onError, 'a', 'z'};
ArdJetInterface aji {ssp, LED_BUILTIN};

void setup() {
    Wire.begin();

    sensor.setModel(MS5837::MS5837_02BA);
    sensor.init();
    
    sensor.setFluidDensity(997); // kg/m^3 (997 freshwater, 1029 for seawater)
    for (int i = 0; i < NUM_MOTORS; i++) {
        motors[i].attach(motor_pins[i]);
        motors[i].writeMicroseconds(1500);
    }

    pinMode(LED_BUILTIN, OUTPUT);   // builtin LED for debugging
    digitalWrite(LED_BUILTIN, LOW);

    ssp.init();
	delay(7000); // delay to allow the ESC to recognize the stopped signal
    aji.awaitConnection(InitChar);
}

void loop() {
    uint16_t motor_values[7];
    bool received = aji.recv_motor_values(motor_values);

    if (received) {
        // Write motor values to ESC
        for (int i = 0; i < NUM_MOTORS; i++) {
            motors[i].writeMicroseconds(motor_values[i]);
        }
    }

    // Continue blinking error
    aji.continue_blinking();
    
    // Pressure sensor read below
    sensor.read();
    aji.send_depth(sensor.pressure());

}

void onError(uint8_t err_num) {
  aji.onError(err_num);
}
