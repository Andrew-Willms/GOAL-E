#include <Servo.h>

/* * WATERLOO MECHATRONICS - ROBUST 3-AXIS CONTROL
 * Rotational: PD Control (10ms Fixed Step) with 96/84 Jump
 * Linear/Vertical: Bidirectional Bang-Bang
 */

// ==========================================
// --- 1. TUNING (ADJUST GAINS HERE) ---
// ==========================================
float Kp = 0.60;           // Start slightly lower with the 96/84 jump
float Kd = 0.05;           // Derivative gain
float alpha = 0.25;        // Filter: 0.0 (full smooth) to 1.0 (no filter)
const float ROT_DEAD = 10.0; // Stop within 1.0 degre

float Kp_L = 120.0;
float Kd_L = 10;
float alpha_L = 0.25;
const double LIN_DEAD = 0.01;

unsigned long switchTime = 0;
// ==========================================
// --- TARGETS & LIMITS ---
// ==========================================
float ROT_TARGET = 20.0;
const float ROT_LIMIT  = 35.0; 

float LIN_TARGET   = 0.2; 
const float LIN_MAX_SAFE = 0.55;
const float LIN_MIN_SAFE = -0.01;

float VERT_TARGET   = 0.0; 
const float VERT_MAX_SAFE = 1000.0;

// ==========================================
// --- CALIBRATION ---
// ==========================================
const float ROT_OFF   = 240.0;
const float LIN_ZERO  = 240.0;
const float VERT_ZERO = 135.0;

// ==========================================
// --- SYSTEM VARIABLES ---
// ==========================================
Servo mRot, mLin, mVert;

volatile unsigned long rStart = 0, rWidth = 0;
volatile unsigned long lStart = 0, lWidth = 0;
volatile unsigned long vStart = 0, vWidth = 0;

float lLast = -1.0; long lRev = 0; bool lInit = false;
float vLast = -1.0; long vRev = 0; bool vInit = false;

// PD Fixed-Step Variables
unsigned long lastProcessTime = 0;
float lastRotError = 0;
double lastLinError = 0;

float filteredDeriv = 0;
double filteredDeriv_L = 0;

int currentRotCmd = 90;
int currentLinCmd = 90;

float currErr = 0;
double currErr_L = 0;

void setup() {
  Serial.begin(115200);

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
  Serial.println("--- 3-AXIS FIXED-STEP PD ONLINE ---");
  delay(3000);
}

void loop() {
  // --- SENSOR PROCESSING (Runs as fast as possible) ---
  
  // 1. ROTATION
  float rRaw = ((constrain(rWidth, 4, 998) - 3.884) / 994.176) * 360.0;
  float rPos = rRaw - ROT_OFF;
  if (rPos > 180.0) rPos -= 360.0;
  if (rPos < -180.0) rPos += 360.0;

  // 2. LINEAR
  float lAng = ((constrain(lWidth, 1, 1024) - 1.0) / 1023.0) * 360.0;
  if (!lInit && lWidth > 0) { lLast = lAng; lInit = true; }
  if (lInit) {
    float diff = lAng - lLast;
    if (diff < -180.0) lRev++; else if (diff > 180.0) lRev--;
    lLast = lAng;
  }

  float lPos = -((lRev * 360.0) + lAng - LIN_ZERO);
  float lPosMetres = (lPos/47.27)/100;

  // 3. VERTICAL
  float vAng = ((constrain(vWidth, 1, 1024) - 1.0) / 1023.0) * 360.0;
  if (!vInit && vWidth > 0) { vLast = vAng; vInit = true; }
  if (vInit) {
    float diff = vAng - vLast;
    if (diff < -180.0) vRev++; else if (diff > 180.0) vRev--;
    vLast = vAng;
  }

  //loop for rotational target
  float vPos = (vRev * 360.0) + vAng - VERT_ZERO;
  if(millis() - switchTime >= 10000){
      ROT_TARGET = -ROT_TARGET;
      switchTime = millis();
  };

  //loop for linear
   if (millis() % 20000 < 10000) {
    LIN_TARGET = 0.2;   // "In"
    VERT_TARGET = 0.0;  // "Down"
  } else {
    LIN_TARGET = 0.4;   // "Out"
    VERT_TARGET = 900;  // "Up"
  }

  // --- CONTROL LOGIC (Runs every 10ms) ---
  if (millis() - lastProcessTime >= 10) {
    float dt = 0.01; // Fixed 10ms step

    // --- ROTATION PD MATH ---
    float rErr = ROT_TARGET - rPos;
    double lErr = LIN_TARGET - lPosMetres;

    if (abs(rErr) <= ROT_DEAD){
      rErr = 0;
    };

    if (abs(lErr) <= LIN_DEAD){
      lErr = 0;
    }

    float rawDeriv = (rErr - lastRotError) / dt;
    double rawDeriv_L = (lErr - lastLinError) / dt;

    filteredDeriv = (alpha * rawDeriv) + ((1.0 - alpha) * filteredDeriv);
    filteredDeriv_L = (alpha_L * rawDeriv_L) + ((1.0 - alpha_L) * filteredDeriv_L);

    float rOut = (Kp * rErr) + (Kd * filteredDeriv);
    double lOut = (Kp_L * lErr) + (Kd_L * filteredDeriv_L);

    // Calculate raw derivative and apply Low-Pass Filter
    if (abs(rErr) > ROT_DEAD) {
      if (rOut > 0) 
        currentRotCmd = 96 + (int)rOut;
      else 
        currentRotCmd = 84 + (int)rOut;
    } else {
      currentRotCmd = 90;
    }

    if (abs(lErr) > LIN_DEAD) {
      if (lOut > 0) 
        currentLinCmd = 80 - (int)lOut;
      else 
        currentLinCmd = 100 - (int)lOut;
    } else {
      currentLinCmd = 90;
    }

    // Safety Checks
    currentRotCmd = constrain(currentRotCmd, 65, 115);
    if (abs(rPos) > ROT_LIMIT) currentRotCmd = 90;
    currentLinCmd = constrain(currentLinCmd, 65, 115);
    if (lPosMetres > LIN_MAX_SAFE){
      currentLinCmd = 90;
    } else if (lPosMetres < LIN_MIN_SAFE){
      currentLinCmd = 90;
    }

    lastRotError = rErr;
    lastLinError = lErr;

    lastProcessTime = millis();
  }

  // --- 4. EXECUTE MOTORS ---
  mRot.write(currentRotCmd);
  mLin.write(currentLinCmd);

  // Linear Bang-Bang
  //int lCmd = 90;
  //if (abs(LIN_TARGET - lPos) > 50.0) lCmd = (LIN_TARGET > lPos) ? 70 : 110;
  //if (lPos > LIN_MAX_SAFE || lPos < -100.0) lCmd = 90;
  //mLin.write(lCmd);

  // Vertical Bang-Bang
  int vCmd = 90;
  if (abs(VERT_TARGET - vPos) > 15.0) vCmd = (VERT_TARGET > vPos) ? 110 : 70;
  if (vPos > VERT_MAX_SAFE || vPos < -100.0) vCmd = 90;
  mVert.write(vCmd);


  // --- 5. TELEMETRY ---
  static unsigned long lastPrint = 0;
  if (millis() - lastPrint > 250) {
    Serial.print("R_Pos:"); Serial.print(rPos, 1);
    Serial.print(" R_Cmd:"); Serial.print(currentRotCmd);
    //Serial.print(" Prev Err:"); Serial.print(lastRotError);
    //Serial.print(" Filt Deriv:"); Serial.print(filteredDeriv);
    //Serial.print(" | L:"); Serial.print(lPos, 0);
    Serial.print(" | LMes:"); Serial.print(lPosMetres);
    Serial.print(" | LinCmd:"); Serial.print(currentLinCmd);
    Serial.print(" Prev Err:"); Serial.print(lastLinError);
    Serial.print(" Filt Deriv:"); Serial.print(filteredDeriv_L);
    Serial.print(" Target:"); Serial.print(LIN_TARGET);
    Serial.print(" | V:"); Serial.println(vPos, 0);
    lastPrint = millis();
  };

}