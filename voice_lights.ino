// Wire LEDs through suitable current-limiting resistors to pins 8, 9, and 10.
// Receives newline-terminated commands such as RED_ON or ALL_OFF over serial.
const byte RED_PIN = 8;
const byte GREEN_PIN = 9;
const byte BLUE_PIN = 10;
String inputLine;

void setup() {
  Serial.begin(9600);
  pinMode(RED_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT);
  pinMode(BLUE_PIN, OUTPUT);
}

void loop() {
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      inputLine.trim();
      handleCommand(inputLine);
      inputLine = "";
    } else {
      inputLine += c;
      if (inputLine.length() > 20) inputLine = "";  // Discard noise.
    }
  }
}

void handleCommand(String command) {
  if (command == "RED_ON") digitalWrite(RED_PIN, HIGH);
  else if (command == "RED_OFF") digitalWrite(RED_PIN, LOW);
  else if (command == "GREEN_ON") digitalWrite(GREEN_PIN, HIGH);
  else if (command == "GREEN_OFF") digitalWrite(GREEN_PIN, LOW);
  else if (command == "BLUE_ON") digitalWrite(BLUE_PIN, HIGH);
  else if (command == "BLUE_OFF") digitalWrite(BLUE_PIN, LOW);
  else if (command == "ALL_ON") {
    digitalWrite(RED_PIN, HIGH);
    digitalWrite(GREEN_PIN, HIGH);
    digitalWrite(BLUE_PIN, HIGH);
  } else if (command == "ALL_OFF") {
    digitalWrite(RED_PIN, LOW);
    digitalWrite(GREEN_PIN, LOW);
    digitalWrite(BLUE_PIN, LOW);
  }
}
