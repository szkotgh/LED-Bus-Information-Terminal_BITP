#include <ArduinoJson.h>

const int LED1 = 3;
const int LED2 = 4;
const int LED3 = 5;
const int LED4 = 6;

const int BUTTON1 = 7;
const int BUTTON2 = 8;

const int RELAY1 = 9;
const int RELAY2 = 10;
const int RELAY3 = 11;
const int RELAY4 = 12;

bool ledStates[] = {false, false, false, false};
bool relayStates[] = {false, false, false, false};

void setup() {
  Serial.begin(115200);

  pinMode(LED1, OUTPUT);
  pinMode(LED2, OUTPUT);
  pinMode(LED3, OUTPUT);
  pinMode(LED4, OUTPUT);

  pinMode(BUTTON1, INPUT_PULLUP);
  pinMode(BUTTON2, INPUT_PULLUP);

  pinMode(RELAY1, OUTPUT);
  pinMode(RELAY2, OUTPUT);
  pinMode(RELAY3, OUTPUT);
  pinMode(RELAY4, OUTPUT);
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    handleCommand(input);
  }
}

void handleCommand(String command) {
  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, command);

  if (error) {
    Serial.println(F("{\"error\":\"Invalid JSON\"}"));
    return;
  }

  if (doc["command"] == "GET_ALL") {
    sendAllStates();
  } else if (doc["command"] == "GET") {
    String variable = doc["variable"];
    sendState(variable);
  } else if (doc["command"] == "SET") {
    String variable = doc["variable"];
    bool state = doc["state"];

    if (variable == "LED1") setLED(LED1, 0, state);
    else if (variable == "LED2") setLED(LED2, 1, state);
    else if (variable == "LED3") setLED(LED3, 2, state);
    else if (variable == "LED4") setLED(LED4, 3, state);
    else if (variable == "RELAY1") setRelay(RELAY1, 0, state);
    else if (variable == "RELAY2") setRelay(RELAY2, 1, state);
    else if (variable == "RELAY3") setRelay(RELAY3, 2, state);
    else if (variable == "RELAY4") setRelay(RELAY4, 3, state);
  }
}

void sendAllStates() {
  StaticJsonDocument<512> doc;
  doc["LED1"] = ledStates[0];
  doc["LED2"] = ledStates[1];
  doc["LED3"] = ledStates[2];
  doc["LED4"] = ledStates[3];
  doc["BUTTON1"] = (digitalRead(BUTTON1) == LOW);
  doc["BUTTON2"] = (digitalRead(BUTTON2) == LOW);
  doc["RELAY1"] = relayStates[0];
  doc["RELAY2"] = relayStates[1];
  doc["RELAY3"] = relayStates[2];
  doc["RELAY4"] = relayStates[3];

  serializeJson(doc, Serial);
  Serial.println();
}

void sendState(String variable) {
  StaticJsonDocument<128> doc;

  if (variable == "LED1") doc[variable] = ledStates[0];
  else if (variable == "LED2") doc[variable] = ledStates[1];
  else if (variable == "LED3") doc[variable] = ledStates[2];
  else if (variable == "LED4") doc[variable] = ledStates[3];
  else if (variable == "BUTTON1") doc[variable] = (digitalRead(BUTTON1) == LOW);
  else if (variable == "BUTTON2") doc[variable] = (digitalRead(BUTTON2) == LOW);
  else if (variable == "RELAY1") doc[variable] = relayStates[0];
  else if (variable == "RELAY2") doc[variable] = relayStates[1];
  else if (variable == "RELAY3") doc[variable] = relayStates[2];
  else if (variable == "RELAY4") doc[variable] = relayStates[3];

  serializeJson(doc, Serial);
  Serial.println();
}

void setLED(int pin, int index, bool state) {
  digitalWrite(pin, state ? HIGH : LOW);
  ledStates[index] = state;
}

void setRelay(int pin, int index, bool state) {
  digitalWrite(pin, state ? HIGH : LOW);
  relayStates[index] = state;
}
