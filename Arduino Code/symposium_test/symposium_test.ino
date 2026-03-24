#include <Servo.h>

/* * WATERLOO MECHATRONICS - FULL 3-AXIS PI CONTROL
 * Rotation: Target via Pi (Sign Flipped)
 * Linear: Target via Pi (Direct Mapping)
 * Vertical: Target via Pi (Mapped 0.27 -> 900 counts)
 */

// --- RS485 COMMS DEFINITIONS ---
#define RS485_DIRECTION_PIN 5
#define RS485_SEND HIGH
#define RS485_RECEIVE LOW
#define START_MESSAGE_FLAG 0

struct target_position {
  uint8_t power;
  float rotation;
  float extension;
  float elevation;
};

union message_data {
  byte raw[sizeof(target_position)];
  target_position target_position;
};

// ==========================================
// --- 1. TUNING GAINS ---
// ==========================================
float Kp = 0.60f;           
float Kd = 0.05f;           
float alpha = 0.25f;        
const float ROT_DEAD = 10.0f; 

float Kp_L = 120.0f;
float Kd_L = 10.0f;
float alpha_L = 0.25f;
const double LIN_DEAD = 0.01;

// ==========================================
// --- TARGETS & LIMITS ---
// ==========================================
float PI_RAW_ROT  = 0.0f;    
float PI_RAW_LIN  = 0.0f;
float PI_RAW_VERT = 0.0f;

float ROT_TARGET  = 0.0f;       
float LIN_TARGET  = 0.0f;  
float VERT_TARGET = 0.0f; 

const float ROT_LIMIT  = 35.0f; 
const float LIN_MAX_SAFE = 0.50f;
const float LIN_MIN_SAFE = 0.0f;
const float VERT_MAX_SAFE = 1000.0f;

// ==========================================
// --- CALIBRATION ---
// ==========================================
const float ROT_OFF   = 240.0f;
const float LIN_ZERO  = 240.0f;
const float VERT_ZERO = 135.0f;

// ==========================================
// --- SYSTEM VARIABLES ---
// ==========================================
Servo mRot, mLin, mVert;

volatile unsigned long rStart = 0, rWidth = 0;
volatile unsigned long lStart = 0, lWidth = 0;
volatile unsigned long vStart = 0, vWidth = 0;

float lLast = -1.0f; long lRev = 0; bool lInit = false;
float vLast = -1.0f; long vRev = 0; bool vInit = false;

unsigned long lastProcessTime = 0;
float lastRotError = 0;
double lastLinError = 0;
float filteredDeriv = 0;
double filteredDeriv_L = 0;

int currentRotCmd = 90;
int currentLinCmd = 90;

void setup() {
  Serial.begin(115200);
  Serial1.begin(115200);

  pinMode(RS485_DIRECTION_PIN, OUTPUT);
  digitalWrite(RS485_DIRECTION_PIN, RS485_RECEIVE);

  mRot.attach(8, 1000, 2000);
  mLin.attach(9, 1000, 2000);
  mVert.attach(10, 1000, 2000);

  pinMode(21, INPUT_PULLUP); pinMode(3, INPUT_PULLUP); pinMode(2, INPUT_PULLUP);

  attachInterrupt(digitalPinToInterrupt(21), []() {
    if (digitalRead(21) == HIGH) rStart = micros();
    else rWidth = micros() - rStart;
  }, CHANGE);

  attachInterrupt(digitalPinToInterrupt(3), []() {
    if (digitalRead(3) == HIGH) lStart = micros();
    else lWidth = micros() - lStart;
  }, CHANGE);

  attachInterrupt(digitalPinToInterrupt(2), []() {
    if (digitalRead(2) == HIGH) vStart = micros();
    else vWidth = micros() - vStart;
  }, CHANGE);

  mRot.write(90); mLin.write(90); mVert.write(90);
  Serial.println("--- 3-AXIS PI CONTROL: ONLINE ---");
  delay(3000);
}

void loop() {
  // --- A. PI COMMUNICATION ---
  if (Serial1.available()) {
    byte first_byte = Serial1.read();
    if (first_byte == START_MESSAGE_FLAG) {
      message_data data;
      int bytes_read = Serial1.readBytes(data.raw, sizeof(target_position));
      if (bytes_read == sizeof(target_position)) {
        // Store Raw Values
        PI_RAW_ROT  = data.target_position.rotation;
        PI_RAW_LIN  = data.target_position.extension;
        PI_RAW_VERT = data.target_position.elevation;

        // Apply Constraints & Mappings
        ROT_TARGET  = constrain(-PI_RAW_ROT, -ROT_LIMIT, ROT_LIMIT);
        LIN_TARGET  = constrain(PI_RAW_LIN, LIN_MIN_SAFE, LIN_MAX_SAFE);
        
        // Vertical Mapping: 0.0 -> 0.0, 0.27 -> 900.0
        // We use 3333.33f as the multiplier (900 / 0.27)
        VERT_TARGET = constrain(PI_RAW_VERT * 3333.33f, 0.0f, VERT_MAX_SAFE);
      }
    }
  }

  // --- B. SENSOR PROCESSING ---
  unsigned long rWidthSafe = constrain(rWidth, 4UL, 998UL);
  float rRaw = ((rWidthSafe - 3.884f) / 994.176f) * 360.0f;
  float rPos = rRaw - ROT_OFF;
  if (rPos > 180.0f) rPos -= 360.0f;
  if (rPos < -180.0f) rPos += 360.0f;

  float lAng = ((constrain(lWidth, 1UL, 1024UL) - 1.0f) / 1023.0f) * 360.0f;
  if (!lInit && lWidth > 0) { lLast = lAng; lInit = true; }
  if (lInit) {
    float diff = lAng - lLast;
    if (diff < -180.0f) lRev++; else if (diff > 180.0f) lRev--;
    lLast = lAng;
  }
  float lPosMetres = (-((lRev * 360.0f) + lAng - LIN_ZERO) / 47.27f) / 100.0f;

  float vAng = ((constrain(vWidth, 1UL, 1024UL) - 1.0f) / 1023.0f) * 360.0f;
  if (!vInit && vWidth > 0) { vLast = vAng; vInit = true; }
  if (vInit) {
    float diff = vAng - vLast;
    if (diff < -180.0f) vRev++; else if (diff > 180.0f) vRev--;
    vLast = vAng;
  }
  float vPos = (vRev * 360.0f) + vAng - VERT_ZERO;

  // --- C. CONTROL LOGIC (10ms Fixed Step) ---
  if (millis() - lastProcessTime >= 10) {
    float dt = 0.01f; 

    // Rotation PD
    float rErr = ROT_TARGET - rPos;
    if (abs(rErr) <= ROT_DEAD) rErr = 0;
    float rawDeriv = (rErr - lastRotError) / dt;
    filteredDeriv = (alpha * rawDeriv) + ((1.0f - alpha) * filteredDeriv);
    float rOut = (Kp * rErr) + (Kd * filteredDeriv);
    if (abs(rErr) > ROT_DEAD) {
      currentRotCmd = (rOut > 0) ? 96 + (int)rOut : 84 + (int)rOut;
    } else { currentRotCmd = 90; }

    // Linear PD
    double lErr = LIN_TARGET - lPosMetres;
    if (abs(lErr) <= LIN_DEAD) lErr = 0;
    double rawDeriv_L = (lErr - lastLinError) / dt;
    filteredDeriv_L = (alpha_L * (float)rawDeriv_L) + ((1.0f - alpha_L) * (float)filteredDeriv_L);
    double lOut = (Kp_L * lErr) + (Kd_L * filteredDeriv_L);
    if (abs(lErr) > LIN_DEAD) {
      currentLinCmd = (lOut > 0) ? 80 - (int)lOut : 100 - (int)lOut;
    } else { currentLinCmd = 90; }

    // Final Constraints
    currentRotCmd = constrain(currentRotCmd, 65, 115);
    if (abs(rPos) > ROT_LIMIT) currentRotCmd = 90;
    currentLinCmd = constrain(currentLinCmd, 65, 115);
    if (lPosMetres > LIN_MAX_SAFE || lPosMetres < LIN_MIN_SAFE) currentLinCmd = 90;

    lastRotError = rErr;
    lastLinError = lErr;
    lastProcessTime = millis();
  }

  // --- D. EXECUTE MOTORS ---
  mRot.write(currentRotCmd);
  mLin.write(currentLinCmd);

  // Vertical Bang-Bang Control
  int vCmd = 95;
  //if (VERT_TARGET - vPos > 15.0f)
  //  vCmd = 105;
  //else if (VERT_TARGET - vPos < -15.0f)
  //  vCmd = 70;

  if (vPos > VERT_MAX_SAFE || vPos < -100.0f)
    vCmd = 90;
  mVert.write(vCmd);

  // --- E. TELEMETRY (DETAILED) ---
  static unsigned long lastPrint = 0;
  if (millis() - lastPrint > 100) {
    // Rotation & Linear (Pi Raw vs Arduino Target)
    Serial.print("R_pi:");   Serial.print(PI_RAW_ROT, 1);
    Serial.print(" L_pi:");   Serial.print(PI_RAW_LIN, 3);
    Serial.print(" V_pi:");   Serial.print(PI_RAW_VERT, 3);
    
    Serial.print(" | R_TRG:"); Serial.print(ROT_TARGET, 1);
    Serial.print(" L_TRG:"); Serial.print(LIN_TARGET, 3);
    Serial.print(" V_TRG:"); Serial.print(VERT_TARGET, 0);

    // Physical Positions
    Serial.print(" | R_POS:"); Serial.print(rPos, 1);
    Serial.print(" L_POS:"); Serial.print(lPosMetres, 3);
    Serial.print(" V_POS:"); Serial.println(vPos, 0);
    
    lastPrint = millis();
  }
}