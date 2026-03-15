#define RS485_DIRECTION_PIN 2
#define RS485_RECEIVE LOW
#define RS485_SEND HIGH
#define START_MESSAGE_FLAG 0

struct target_position {
  uint16_t rotation;
  uint16_t extension;
  uint16_t elevation;
};

union message_data {
  byte raw[sizeof(target_position)];
  target_position target_position;
};

void setup() {

  pinMode(RS485_DIRECTION_PIN, OUTPUT);
  digitalWrite(RS485_DIRECTION_PIN, RS485_RECEIVE);
  
  Serial.begin(115200);
  Serial1.begin(115200);

  Serial.println("setup complete");
}

void loop() {

  if (Serial1.available()) {

    byte first_byte = Serial1.read();
    if (first_byte != START_MESSAGE_FLAG) {
      Serial.print("Error in flag byte - Expected: ");
      Serial.print(START_MESSAGE_FLAG);
      Serial.print(" Recieved: ");
      Serial.println(first_byte);
      return;
    }

    message_data data;
    int bytes_read = Serial1.readBytes(data.raw, sizeof(target_position));

    if (bytes_read != sizeof(target_position)) {
      Serial.print("Error in message length - Expected: ");
      Serial.print(sizeof(target_position));
      Serial.print(" Recieved: ");
      Serial.println(bytes_read);
      return;
    }

    Serial.print("Received: ");
    Serial.print(data.target_position.rotation);
    Serial.print(", ");
    Serial.print(data.target_position.extension);
    Serial.print(", ");
    Serial.println(data.target_position.elevation);
  }
}