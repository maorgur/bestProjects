
#include "ScreenManager.hpp"
#include <Arduino.h>
#include <LiquidCrystal_I2C.h>
#include <string>

#define DIRECTION_CHANGE 0b00011110

byte unknownChar[] = {
  B11111,
  B10001,
  B10001,
  B10001,
  B10001,
  B10001,
  B10001,
  B11111
};
byte gimel[] = {
  B00000,
  B00000,
  B01100,
  B00010,
  B00010,
  B00110,
  B01010,
  B01010
};
byte dalet[] = {
  B00000,
  B00000,
  B11111,
  B00010,
  B00010,
  B00010,
  B00010,
  B00010
};
byte hey[] = {
  B00000,
  B11110,
  B00001,
  B00001,
  B00001,
  B11001,
  B01001,
  B01001
};
byte tzadik[] = {
  B00000,
  B00000,
  B10001,
  B01010,
  B00100,
  B00010,
  B00001,
  B01111
};
byte lamed[] = {
  B00000,
  B01000,
  B01000,
  B01111,
  B00001,
  B00010,
  B00100,
  B01000
};
byte tet[] = {
  B00000,
  B00000,
  B10001,
  B10011,
  B10101,
  B10001,
  B10001,
  B11110
};

struct CharMap {
    uint16_t unicode;
    char replacement;
};



CharMap mappings[] = {
    {0x05D0, 0b11010010},      // א
    {0x05D1, 0b11010101}, // ב
    {0x05D2,  1},        // ג custom
    {0x05D3, 2}, // ד custom
    {0x05D4, 3}, // ה custom
    {0x05D5, '|'}, // ו
    {0x05D6, 'T'},      // ז
    {0x05D7, 'n'},      // ח
    {0x05D8, 6}, // ט custom
    {0x05D9, 0b11011111}, // י
    {0x05DB, 0b10111010}, // כ
    {0x05DC, 5}, // ל custom
    {0x05DE, 0b10111000}, // מ
    {0x05E0, 0b11001001}, // נ
    {0x05E1, 'o'}, // ס
    {0x05E2, 0b10111111}, // ע
    {0x05E4, '@'}, // פ
    {0x05E6, 4}, // צ custom
    {0x05E7, 0b10110001}, // ק
    {0x05E8, 0b11001101}, // ר
    {0x05E9, 'w'}, // ש
    {0x05EA, 0b10110110}  // ת
    ,
    {0x05DA, 0b10111010}, // ך (same as כ)
    {0x05DD, 0b10111000}, // ם (same as מ)
    {0x05DF, 0b11001001}, // ן (same as נ)
    {0x05E3, '@'},  // ף (same as פ)
    {0x05E5, 4},  // ץ custom (same as צ)


};

void Screen::init() {
    LiquidCrystal_I2C::init();
    LiquidCrystal_I2C::home();
    LiquidCrystal_I2C::backlight();
    LiquidCrystal_I2C::createChar(0, unknownChar);
    LiquidCrystal_I2C::createChar(1, gimel);
    LiquidCrystal_I2C::createChar(2, dalet);
    LiquidCrystal_I2C::createChar(3, hey);
    LiquidCrystal_I2C::createChar(4, tzadik);
    LiquidCrystal_I2C::createChar(5, lamed);
    LiquidCrystal_I2C::createChar(6, tet);
}

void Screen::printToScreen(const char* text, int justify, bool debug){
    //justify -1 to left, 0 to center and 1 to right

    currentText = ConvertUTF8String((char*)text); //will also act as copying the text
    splitToLines(currentText);


    //init vars
    int currentCol = 0, currentRow = 0;
    int textSize = strlen(currentText);
    memset(currentLine, 0, 100);
          
    LiquidCrystal_I2C::home(); //set cursor to 0,0 and the scroll
              
    //go check by char, and iadd it to the line. if finished line, print it
    for (int i = 0; i < textSize; i++){
        if (currentText[i] == '\n'){
            printLine(currentLine, currentRow, justify);
        
            memset(currentLine, 0, 100);
        
            currentCol = 0;
            currentRow ++;
            continue;
        }
    
        currentLine[currentCol] = currentText[i];
        currentCol ++;
    }
    printLine(currentLine, currentRow, justify);

    if (debug){
        Serial.println(currentText);
    }
}
void Screen::turnOn(){
    Screen::clear();
    Screen::backlight();
    Screen::noCursor();
    prevText[0] = 0;

}

void Screen::turnOff(){
    Screen::noBacklight();
    Screen::clear();
    Screen::noCursor();
    prevText[0] = 0;
}
        

void Screen::printLine(char* line, int row, int justify){
    //will add spaces at the end of the line if needed
    //assuming line has a buffer of atleast 17 chars

    if (justify == 0){
        centerText(line);
    } else if (justify > 0){
        rightText(line);
    } //no need to justify left, that's the default for text

    int lineLen = strlen(line);
    if (lineLen < 40){
        memset(line+lineLen, ' ', 40-lineLen);
    }
    line[40] = '\0';

    
    LiquidCrystal_I2C::setCursor(0, row);
    for (int i = 0; i < 16; i++){ //not using print bcs of custom chars
        LiquidCrystal_I2C::write(line[i]);
    }
}



void Screen::centerText(char* text) {
    //assumes that text has a buffer of atleast 16
    //won't add spaces after the text

    int normalLength = strlen(text);

    int padding = (16 - normalLength)/2;
    //the text is long enough, nothing to center
    if (padding <= 0){return;}

    //+1 to accomedate the \0
    memmove(text + padding, text, normalLength+1);
    //add the padding
    memset(text, ' ', padding*sizeof(char));

}


void Screen::rightText(char* text) {
    //assumes that text has a buffer of atleast 16
    //won't add spaces after the text

    int normalLength = strlen(text);

    int padding = 16 - normalLength;
    //the text is long enough, nothing to right align
    if (padding <= 0){return;}

    //+1 to accomedate the \0
    memmove(text + padding, text, normalLength+1);
    //add the padding
    memset(text, ' ', padding*sizeof(char));

}

void Screen::splitToLines(char* text){
    //will try to split the text to different lines where possible, if not, will cut text.
    //assumes that text doesnt take all of the buffer, atleast 1 available byte at the end
    int stringLength = strlen(text);
    if (stringLength <= 16){//nothing to split, but add another line bcs it will clear the second line and stuff
        return;
        } 
    for (int i = 0; i < stringLength; i++){
        if (text[i] == '\n'){
            return; // text was already externally formatted
        }
    }
    
    for (int i = 15; i > 0; i--){
        if (text[i] == ' ' || text[i] == '\n'){
            //found a good place to split, splitting and returning
            text[i] = '\n';
            return;
        }
    }

    //if the for loop ended, it means no good place to cut has been found, so force a cut (ugly)
    memmove(text+17, text+16, stringLength-16+1); //+1 for \0
    text[16] = '\n';
    return;

}

typedef struct {
    int direction; //-1 for RTL, 1 for LTR, 0 for neutral
    bool addToCount; //for when deciding the main direction, if to count the direction of this char or not
} directionData;

directionData getDirection(char letter){
    //first check if it's completely neutral
    if ((letter >= ' ' && letter <= '/') || (letter >= ':' && letter <= '@') || (letter >= '[' && letter <= '`') || (letter >= '{' && letter <= '~') || letter == '\n'){
        return {0, false};
    }

    //check if it's a number
    if (letter >= '0' && letter <= '9'){
        return {1, false}; //numbers are usually LTR, but we won't count them when deciding the direction of the text
    }
    
    //check if it's an eng letter
    if ((letter >= 'A' && letter <= 'Z') || (letter >= 'a' && letter <= 'z')){
        return {1, true};
    }

    //check if it's a Hebrew character (Unicode range 0x0590-0x05FF)
    if ((unsigned char)letter >= 0x80) { // Multi-byte UTF-8 or high byte
        return {-1, true}; // Assume RTL for non-ASCII characters
    }

    //default to LTR for unknown characters
    return {1, false};
}

char* Screen::ConvertUTF8String(char* text, bool addDirectionMarks){
    //makes sure all of the chars are supported, if not it will get replaced by the unknown char
    //handles multi-byte UTF-8 sequences properly
    memset(convertedResult, 0, 100);
    int resultIndex = 0;

    bool currentlyLTR = true;
    int lastStrongDirectionCharIndex = 0;
    for (int i = 0; text[i] != '\0' && i < 100; i++){ 
        unsigned char byte = text[i];

        //perform direction check
        if (addDirectionMarks){

            ////for newline, there is a special case cuz it needs to split exactly in the correct place
            //if (!currentlyLTR && text[i] == '\n'){
            //    convertedResult[resultIndex++] = DIRECTION_CHANGE;
            //    convertedResult[resultIndex++] = '\n';
            //    convertedResult[resultIndex++] = DIRECTION_CHANGE;
            //}

            int letterDirection = getDirection(text[i]).direction;


            if ((letterDirection == -1 && currentlyLTR) || (letterDirection == 1 && !currentlyLTR)){
                //insert direction change, BUT add it after the last strong direction char, that makes sure that spaces and new lines wouldn't get flipped
                //if it's the start of RTL, then insert here
                if (letterDirection == 1){
                    memmove(convertedResult + lastStrongDirectionCharIndex+1, convertedResult + lastStrongDirectionCharIndex, resultIndex - lastStrongDirectionCharIndex+1);
                    convertedResult[lastStrongDirectionCharIndex+1] = DIRECTION_CHANGE;
                    resultIndex++;
                    //convertedResult[resultIndex++] = DIRECTION_CHANGE;
                    currentlyLTR = true;
                } else if (letterDirection == -1){
                    convertedResult[resultIndex++] = DIRECTION_CHANGE;
                    currentlyLTR = false;
                }

            }

            if (letterDirection != 0){lastStrongDirectionCharIndex = resultIndex;}

        }
        
        // Check if this is a multi-byte UTF-8 sequence start
        if (byte >= 0xC0) { // Multi-byte UTF-8 character
            int charLen = 0;
            uint16_t unicode = 0;
            
            if ((byte & 0xE0) == 0xC0) { // 2-byte sequence
                charLen = 2;
                unicode = ((uint16_t)(byte & 0x1F) << 6) | (text[i+1] & 0x3F);
            } else if ((byte & 0xF0) == 0xE0) { // 3-byte sequence
                charLen = 3;
                unicode = ((uint16_t)(byte & 0x0F) << 12) | 
                         ((uint16_t)(text[i+1] & 0x3F) << 6) | 
                         (text[i+2] & 0x3F);
            } else if ((byte & 0xF8) == 0xF0) { // 4-byte sequence
                charLen = 4;
                unicode = ((uint32_t)(byte & 0x07) << 18) | 
                         ((uint32_t)(text[i+1] & 0x3F) << 12) | 
                         ((uint32_t)(text[i+2] & 0x3F) << 6) | 
                         (text[i+3] & 0x3F);
            } else {
                
            // Invalid UTF-8 start byte, treat as unknown char
            Serial.printf("Invalid UTF-8 start byte: %02X, masking: %02x", byte, byte & 0xE0);
            unicode = 0xFFFD; // Unicode replacement character   
            }

            char replacement = 0;
            
            int numMappings = sizeof(mappings) / sizeof(mappings[0]);
            for (int k = 0; k < numMappings; k++){
                if (mappings[k].unicode == unicode){
                    replacement = mappings[k].replacement;
                    break;
                }
            }

            convertedResult[resultIndex++] = replacement;
            i += charLen -1;


        } else {
            convertedResult[resultIndex++] = text[i];
        }
    }
    if (!currentlyLTR){
        //if the text ended while we were in RTL, add a direction mark at the end to prevent the LCD from messing with the text
        convertedResult[resultIndex++] = DIRECTION_CHANGE;
    }
    if (addDirectionMarks){
        return applyDirectionOnLineWithAnnotations(convertedResult);
    }
    return convertedResult;
}



char* Screen::applyDirectionOnLineWithAnnotations(char* line){
    //will search for encapsulated DIRECTION_CHANGE and reverse the text inside
    memset(directionalResult, 0, 100);
    int resultIndex = 0;
    bool reverse = false;
    
    char* reversedEnd;
    int reversedIndex;

    for (int i = 0; line[i] != '\0'; i++){
        if (!reverse){
            if (line[i] != DIRECTION_CHANGE){
                directionalResult[resultIndex++] = line[i];
            } else {
                //set the reversed variables, and handle edge case
                reversedEnd = strchr(line+i+1, DIRECTION_CHANGE);
                if (reversedEnd == NULL){
                    Serial.println("failure while applying the direction of a text, didn't found an ending to a reversed part. cancelled reversion completely");
                    return line;
                }
                reversedIndex = 1;
                reverse = true;
            }
        } else {
            if (*(reversedEnd-reversedIndex) != DIRECTION_CHANGE){
                directionalResult[resultIndex++] = *(reversedEnd-reversedIndex);
                reversedIndex++;

            } else {
                reverse = false;
            }
        }
    }
    return directionalResult;
}

void Screen::testCustomChars(){
    
    char testText[100];
    memset(testText, 0, 100); //to make sure
    int x;
    LiquidCrystal_I2C::clear();
    LiquidCrystal_I2C::home();
    int numMappings = sizeof(mappings) / sizeof(mappings[0]);
    for (x = 0; x < numMappings; x++){ 
        if (x == 14){
            LiquidCrystal_I2C::setCursor(0, 1);
        }
        testText[x] = mappings[x].replacement;
        Serial.printf("Testing char: %04X, %c\n", mappings[x].unicode, mappings[x].replacement);
        LiquidCrystal_I2C::write(mappings[x].replacement);
    }
    
    Serial.println(testText);
}
