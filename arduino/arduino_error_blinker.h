#pragma once
#include <Arduino.h>
#include <SimpleSerialProtocol.h>

class ErrorBlinker {
    public:
    ErrorBlinker(uint8_t led) : led_num(led) {}
    enum class ErrorType {
        None,
        Timeout,
        Connecting,
        Generic
    };

    private:
    ErrorType current_error;
    int generic_pattern[2] = {100, 100};
    int timeout_pattern[4] = {200, 200, 200, 400};
    int connecting_pattern[4] = {100, 100, 500, 400};
    unsigned long start_time_mark;
    int array_index;
    int n_rep;
    uint8_t led_num;

    public:
    void blink_generic() { blink_error(ErrorType::Generic); }
    void blink_timeout() { blink_error(ErrorType::Timeout); }
    void blink_connecting() { blink_error(ErrorType::Connecting); }
    void continue_blinking() { blink_error(current_error); };

    void set(bool val) { digitalWrite(led_num, val); }

    private:
    void blink_error(const ErrorType err_type);
    bool blink_pattern(const int wait_values[], const int length, const int repetitions);
};


void ErrorBlinker::blink_error(const ErrorType err_type) {
    if (err_type == ErrorType::None) return;

    if (current_error == ErrorType::None) {
        start_time_mark = millis();
    }
    if (current_error == err_type || current_error == ErrorType::None) {
        bool complete;
        current_error = err_type;
        switch (err_type)
        {
        case ErrorType::Generic:
            complete = blink_pattern(generic_pattern,
                                     sizeof(generic_pattern)/sizeof(generic_pattern[0]),
                                     2);
            break;
        case ErrorType::Timeout:
            complete = blink_pattern(timeout_pattern,
                                     sizeof(timeout_pattern)/sizeof(timeout_pattern[0]),
                                     5);
            break;
        case ErrorType::Connecting:
            complete = blink_pattern(connecting_pattern,
                                     sizeof(connecting_pattern)/sizeof(timeout_pattern[0]),
                                     1);
        default:
            break;
        }

        if (complete) {
            set(LOW);
            current_error = ErrorType::None;
        }
    }
}

bool ErrorBlinker::blink_pattern (const int wait_values[], const int length, const int repetition) {
    unsigned long current_time = millis();
    static int rep_num = 0;
    if (current_time - start_time_mark > wait_values[array_index]) {
        // Go to the next segment
        array_index++;
        start_time_mark = current_time;
        if (array_index >= length) {
            // If this is the last element, return true (complete)
            array_index = 0;
            rep_num++;

            if (rep_num >= repetition) {
                return true;
            }
        }
    }

    if (array_index % 2) {
        digitalWrite(led_num, LOW);
    } else {
        digitalWrite(led_num, HIGH);
    }

    return false;
}