#define RS485_DIR 2

void setup() {
  pinMode(RS485_DIR, OUTPUT);
  
  digitalWrite(RS485_DIR, LOW);   // start in receive mode
  
  Serial.begin(115200);           // USB debug
  Serial1.begin(115200);            // RS485 UART

  Serial.println("setup complete");
}

void loop() {

  if (Serial1.available()) {

    byte start_flag = Serial1.read();
    if (start_flag != 0) {
      Serial.print("Out of alignment.");
      return;
    }

    byte message_buffer[2];
    int bytes_read = Serial1.readBytes(message_buffer, 2);

    if (bytes_read != 2) {
      Serial.print("Missing bytes.");
      return;
    }

    uint16_t message = ((uint16_t)message_buffer[0] << 8) | message_buffer[1];
    Serial.print("Received: ");
    Serial.println(message);
  }
}