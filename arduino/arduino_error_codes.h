#pragma once
#include <Arduino.h>

namespace BlinkPatterns {
    void blink_pattern(const int wait_values[], const int repetitions);

    int error_pattern[2] = {100, 100};
    void blink_error() { blink_pattern(error_pattern, 10); }

    int timeout_pattern[2] = {10, 10};
    void blink_timeout() { blink_pattern(timeout_pattern, 1); }
    
    int connecting_pattern[4] = {50, 50, 50, 100};
    void blink_connecting() { blink_pattern(connecting_pattern, 1); }
};

void BlinkPatterns::blink_pattern (const int wait_values[], const int repetition) {
    int length = sizeof(wait_values) / sizeof(wait_values[0]);
    for (int i = 0; i < length; i++) {
        digitalWrite(LED_BUILTIN, HIGH);
        delay(wait_values[i]);
        if (i + 1 >= length) {
            break;
        }
        digitalWrite(LED_BUILTIN, LOW);
        delay(wait_values[++i]);
    }
    digitalWrite(LED_BUILTIN, LOW);
}