#include <Arduino.h>
#include <Servo.h>

Servo tiltServo;
Servo panServo;

// Neutral position for servos in degrees
int tiltNeutral = 75;
int panNeutral = 100;

int lastTiltAngle = 0;
int lastPanAngle = 0;

// Angle for quick look to left/right
int lookAngle = 60;
bool lookToLeftSide = false;
bool lookToRightSide = false;

unsigned long lastCommandTime = 0;  // Last time a command was received
unsigned long returnDelay = 100;   // Time (in ms) before returning to neutral position

void setup() {
  Serial.begin(9600);
  tiltServo.attach(9);  // Connect servo 1 to pin 9
  panServo.attach(10); // Connect servo 2 to pin 10

  // Initialize servos to neutral position
  tiltServo.write(tiltNeutral);
  panServo.write(panNeutral);

  // Update last angles
  lastPanAngle = panNeutral;
  lastTiltAngle = tiltNeutral;
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');  // Read the command

    if (command == "s0") {
      tiltServo.write(tiltNeutral); // Set servo 1 to neutral position
      lastTiltAngle = tiltNeutral; // Update last angle

      panServo.write(panNeutral); // Set servo 2 to neutral position
      lastPanAngle = panNeutral; // Update last angle
    }
    if (command == "s1") {
      lastTiltAngle = constrain(lastTiltAngle + 1, 0, 180); // Ensure angle stays between 0 and 180
      tiltServo.write(lastTiltAngle); // Increment servo 1 angle by +1
    }
    if (command == "s2") {
      lastTiltAngle = constrain(lastTiltAngle - 1, 0, 180); // Ensure angle stays between 0 and 180
      tiltServo.write(lastTiltAngle); // Decrement servo 1 angle by -1
    }
    if (command == "s3") {
      // lastPanAngle = constrain(lastPanAngle + 1, 0, 180); // Ensure angle stays between 0 and 180
      // panServo.write(lastPanAngle); // Increment servo 2 angle by +1

      if (lookToLeftSide == false || lookToRightSide == true) {
        lookToLeftSide = true;
        lookToRightSide = false;
        panServo.write(panNeutral + lookAngle); // Look to the left
        lastCommandTime = millis();
      }
    }
    if (command == "s4") {
      // lastPanAngle = constrain(lastPanAngle - 1, 0, 180); // Ensure angle stays between 0 and 180
      // panServo.write(lastPanAngle); // Decrement servo 2 angle by -1

      lastCommandTime = millis();  // Update last command time
      if (lookToRightSide == false || lookToLeftSide == true) {
        lookToRightSide = true;
        lookToLeftSide = false;
        panServo.write(panNeutral - lookAngle); // Look to the right
        lastCommandTime = millis();
      }
    }
    // If no command was received for a while, return to neutral position
    if ((millis() - lastCommandTime > returnDelay) && (lookToLeftSide || lookToRightSide)) {
      panServo.write(panNeutral);  // Move pan back to neutral
      lastPanAngle = panNeutral;
      lookToLeftSide = false;
      lookToRightSide = false;

      delay(200);  // Wait for the servo to reach the neutral position
      // panServo.detach();  // Detach the servo to stop it from auto adjusting
    }
  }
}