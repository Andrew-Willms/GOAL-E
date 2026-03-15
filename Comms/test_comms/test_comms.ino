#define RS485_DIR 2

void setup() {
  pinMode(RS485_DIR, OUTPUT);
  
  digitalWrite(RS485_DIR, LOW);   // start in receive mode
  
  Serial.begin(115200);           // USB debug
  Serial1.begin(115200);            // RS485 UART

  Serial.println("setup complete");
}

void loop() {

  // transmit
  //digitalWrite(RS485_DIR, HIGH);

  //Serial1.println("Hello RS485");

  //Serial1.flush();                // wait for transmission

  //digitalWrite(RS485_DIR, LOW);   // back to receive

  // receive
  if (Serial1.available()) {
    Serial.println("serial is available");

    byte msg = Serial1.read();

    //String msg = Serial1.readString();
    Serial.println(msg);
  }
}