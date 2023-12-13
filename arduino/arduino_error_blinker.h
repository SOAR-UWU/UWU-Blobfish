#pragma once
#include <Arduino.h>
#include <SimpleSerialProtocol.h>

/**
 * Implementation of a blinker for displaying errors on the Arduino.
 * 
 * The given LED (specified on initialisation) is blinked in a pattern specified in
 * an int array (numbers are in ms). If another error occurs while midway through a
 * blink pattern, the new error is ignored.
 * 
 * The blink functions are NON-BLOCKING. The function continue_blinking has to be
 * continuously called to ensure the LED is updated.
*/
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
    ErrorType current_error;    ///> Error type of currently blinking error (if any)
    const int generic_pattern[4] = {200, 100, 200, 100};  ///> Default blink pattern
    const int timeout_pattern[6] = {100, 100, 100, 100, 100, 400};    ///> Timed out waiting for input
    const int connecting_pattern[4] = {100, 100, 500, 400};   ///> Awaiting connection
    unsigned long start_time_mark;  ///> Time of start of current section
    int current_section_index;  ///> Index number of current section
    const uint8_t led_num;    ///> Pin number of LED

    public:
    void blink_generic() { blink_error(ErrorType::Generic); }
    void blink_timeout() { blink_error(ErrorType::Timeout); }
    void blink_connecting() { blink_error(ErrorType::Connecting); }

    /**
     * @brief Continue blinking the current error pattern
     */
    void continue_blinking() { blink_error(current_error); };

    /**
     * @brief Set the error LED on or off.
     * 
     * @param val HIGH or LOW
     */
    void set(bool val) { digitalWrite(led_num, val); }

    private:
    /**
     * @brief Blink the code of the given error type, if one is not already blinking
     * 
     * @param err_type Type of error
     */
    void blink_error(const ErrorType err_type);

    /**
     * @brief Blink the LED in the given pattern
     * 
     * The LED is flashed alternatively ON and OFF until the pattern is complete. For example,
     * the pattern [100, 300, 200, 500] means:
     * 
     * - ON for 100ms
     * - OFF for 300ms
     * - ON for 200ms
     * - OFF for 500ms
     * 
     * @param wait_values Pattern to blink. Entries with even indices are ON, entries with
     * odd indices are OFF.
     * @param length Length of int array
     * @return true if the pattern has been completed, false if not
     */
    bool blink_pattern(const int wait_values[], const int length);
};


void ErrorBlinker::blink_error(const ErrorType err_type) {
    // If no error is submitted, return immediately
    if (err_type == ErrorType::None) return;

    if (current_error == ErrorType::None) {
        // If there is no error being blinked at the moment, set the start time
        start_time_mark = millis();
    }
    if (current_error == err_type || current_error == ErrorType::None) {
        // Only blink the submitted error if there is no current error or if the submitted
        // error is the same as the current error
        bool complete;
        current_error = err_type;
        switch (err_type)
        {
        case ErrorType::Generic:
            complete = blink_pattern(generic_pattern,
                                     sizeof(generic_pattern)/sizeof(generic_pattern[0]));
            break;
        case ErrorType::Timeout:
            complete = blink_pattern(timeout_pattern,
                                     sizeof(timeout_pattern)/sizeof(timeout_pattern[0]));
            break;
        case ErrorType::Connecting:
            complete = blink_pattern(connecting_pattern,
                                     sizeof(connecting_pattern)/sizeof(timeout_pattern[0]));
        default:
            break;
        }

        if (complete) {
            // Current error is done blinking
            set(LOW);
            current_error = ErrorType::None;
        }
    }
}

bool ErrorBlinker::blink_pattern (const int wait_values[], const int length) {
    unsigned long current_time = millis();
    if (current_time - start_time_mark > wait_values[current_section_index]) {
        // Go to the next segment
        current_section_index++;
        start_time_mark = current_time;
        if (current_section_index >= length) {
            // If this is the last element, return true (complete)
            current_section_index = 0;
            return true;
        }
    }

    if (current_section_index % 2) {
        digitalWrite(led_num, LOW);
    } else {
        digitalWrite(led_num, HIGH);
    }

    return false;
}