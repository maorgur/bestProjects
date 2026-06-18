#pragma once

#include <Arduino.h>
#include <LiquidCrystal_I2C.h>
#include <string>

class Screen: public LiquidCrystal_I2C{ //adapter design pattern
    public:
        Screen(): LiquidCrystal_I2C(0x27, 16, 2){}

        void init();

        void printToScreen(const char* text, int justify=0, bool debug = false);

        template<typename... Args>
        void printToScreenf(int justify, bool debug, const char* format, Args... args) {
            char buffer[100];
            sprintf(buffer, format, args...);
            printToScreen(buffer, justify, debug);
        }

        void testCustomChars();

        void turnOn();
        void turnOff();

    private:

        //for centerText
        static const int textBox = 16;
        //for printToScreen
        char currentLine[100];
        char prevText[100];
        char* currentText;
        

        void printLine(char* line, int row=0, int justify=-1);

        static void centerText(char* text);
        static void rightText(char* text);

        static void splitToLines(char* text);

        char convertedResult[100];
        char* ConvertUTF8String(char* text, bool addDirectionMarks = true);
        
        char directionalResult[100];
        char* applyDirectionOnLineWithAnnotations(char* line);

};
