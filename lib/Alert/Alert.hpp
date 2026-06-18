#pragma once

#include <Arduino.h>
#include <string>

void alertSetup();

void light_for_time(int time);
void buzz_for_time_and_freq(int time, int freq, bool light);

void double_light();
void double_buzz(int freq);

void double_light_at_right_time(int hour);
void light_at_right_time(int hour, int time);
void double_buzz_at_right_time(int hour, int freq, bool light);

void doubleBuzzBasedTimeAndPriority(int hour, int priority);
void smartAircraftAlert(int hour, const std::string& aircraft);
