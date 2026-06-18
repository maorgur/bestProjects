#include <Alert.hpp>
#include <map>

#define BUZZER_PIN 15
#define LED_PIN 12
#define BUZZ_MIN_HOUR 9
#define BUZZ_MAX_HOUR 19

const std::map<std::string, int> priority_map = { //0,1 will activate buzzer and LED, 2 will only activate LED
    {"C5M", 0}, //C-5 super galaxy
    {"U2", 0},
    {"F35", 0},
    {"F15", 0},
    {"F16", 0},
    {"EUFI", 1}, //eurofighter
    {"B52", 0},
    {"B2", 0},
    {"B1", 0},
    {"R135", 1}, //rc-135 reconnaissance plane
    {"K35R", 2}, //stratotaneker
    {"E3TF", 1}, {"E3CF", 1}, //E3-sentry
    {"P8", 1}, //P-8 poseidon
    {"C130", 1}, //C-130 hercules
    {"C17", 1}, //C-17 globemaster
    {"B703", 1}, //israeli tanker
};

void alertSetup(){
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);
  digitalWrite(LED_PIN, LOW);
}

void light_for_time(int time){
  digitalWrite(LED_PIN, HIGH);
  delay(time);
  digitalWrite(LED_PIN, LOW);
}

void buzz_for_time_and_freq(int time, int freq, bool light){
    if (light){
        digitalWrite(LED_PIN, HIGH);
    }
    tone(BUZZER_PIN, freq, time);  
    if (light){
        delay(time);
        digitalWrite(LED_PIN, LOW);
    }
}


void double_light(){
  light_for_time(50);
  delay(100);
  light_for_time(50);
}

void double_buzz(int freq, bool light){
    //will buzz for 50ms twice
    if (freq <= 0){freq = 100;} //min freq that can be heard

    buzz_for_time_and_freq(50, freq, light);
    delay(100);
    buzz_for_time_and_freq(50, freq, light);
}

void double_light_at_right_time(int hour){
    if (hour >= BUZZ_MIN_HOUR && hour <= BUZZ_MAX_HOUR){
        double_light();
    }
}

void light_at_right_time(int hour, int time){
    if (hour >= BUZZ_MIN_HOUR && hour <= BUZZ_MAX_HOUR){
        light_for_time(time);
    }
}

void double_buzz_at_right_time(int hour, int freq, bool light){
    if (hour >= BUZZ_MIN_HOUR && hour <= BUZZ_MAX_HOUR){
        double_buzz(freq, light);
    }
}


void doubleBuzzBasedTimeAndPriority(int hour, int priority){
    //priority 0 is 1000Hz, 1 is 900Hz, 2 is 800Hz and so on.
    //if priority is 0 or 1, it will double buzz 3 times
    if (priority == 0){
        double_buzz_at_right_time(hour, 1000, true);
        delay(200);
        double_buzz_at_right_time(hour, 1000, true);
        delay(200);
        double_buzz_at_right_time(hour, 1000, true);
    } else if (priority == 1){
        double_light_at_right_time(hour);
    } else {
        light_at_right_time(hour, 500);
    }
}

void smartAircraftAlert(int hour, const std::string& aircraft){
    auto it = priority_map.find(aircraft);
    if (it != priority_map.end()){
        int priority = it->second;
        Serial.printf("Alerting for aircraft %s with priority %d\n", aircraft.c_str(), priority);
        doubleBuzzBasedTimeAndPriority(hour, priority);
    } else {
        return;
    }
}
