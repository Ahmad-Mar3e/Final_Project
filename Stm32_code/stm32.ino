#include <Servo.h>
#include <DHT.h>
Servo myservo;

DHT sense(PB9,DHT22);

int trig = PB12; //for ultrasonic
int echo = PB13; //for ultrasonic
int detect = PB3; // led when object is near
int radiat = PA0; // the pin connect to ldr voltage divider
int radiant_detect = PA1; //led for radiaton 
int led_1 = PC13;  //led for temperature 
int led_2 = PC14;  //led for temperature
int led_3 = PC15;  //led for temperature

long travel_time; // for ultrasonic
int distance; // distance of the object
int angle;  // angle of servo
float temp_value; // teperature value
int ldr_value ;  // radiation value
int object_detect = 0
String msg ; // msg from serial


void setup() {
  myservo.attach(PB11);
  pinMode(trig, OUTPUT);
  pinMode(echo, INPUT);
  pinMode(detect, OUTPUT);
  pinMode(radiant_detect, OUTPUT);
  myservo.write(0);
  Serial.begin(9600);  
  pinMode(led_1, OUTPUT);
  pinMode(led_2, OUTPUT);
  pinMode(led_3, OUTPUT);
  sense.begin();


}

void loop() {
  msg = read();
   if (msg == "on") {
    system_on();
  } 
  else if (msg == "off") {
    stopSystem();
  }
}



void system_on(){
  while (1){
   for (int i = 0; i <= 180; i++) {
    angle = i;
    myservo.write(i);
    checkDistance(); 
    radiation();
    temperature();
    read_sensors();
    msg = read();
    if (msg == "off") {
      stopSystem();
      return;
    }
    delay(30);
  }

  for (int i = 180; i >= 0; i--) {
    angle = i;
    myservo.write(i);
    checkDistance(); 
    radiation();
    temperature();
    read_sensors();
    msg = read();
    if (msg == "off") {
      stopSystem();
      return;
    }
    delay(30);
  }
}
}


void stopSystem(){
  myservo.write(0);             
  digitalWrite(detect, LOW);     
  digitalWrite(radiant_detect, LOW);
  digitalWrite(led_1, LOW);
  digitalWrite(led_2, LOW);
  digitalWrite(led_3, LOW);
  msg = "";
}




void checkDistance() {
 
  digitalWrite(trig, LOW);
  delayMicroseconds(2);
  digitalWrite(trig, HIGH);
  delayMicroseconds(10);
  digitalWrite(trig, LOW);

  travel_time = pulseIn(echo, HIGH);
  distance = travel_time * 0.0343 / 2;

  if (distance < 50) {
    digitalWrite(detect, HIGH);
    object_detect = 1;
  } 
  else {
    digitalWrite(detect, LOW);
    object_detect = 0;
  }
 
}



void radiation(void){
  ldr_value = analogRead(radiat);
  if ( ldr_value <110 ){
  digitalWrite(radiant_detect,HIGH);
  
  }
  else{
     digitalWrite(radiant_detect,LOW);
  }
  }


  void temperature(void){


   temp_value = sense.readTemperature();
   if (temp_value<20){
    digitalWrite(led_1,HIGH);
    digitalWrite(led_2,LOW);
    digitalWrite(led_3,LOW);

   }
   else if (temp_value >= 20 && temp_value <= 30 ) {
    digitalWrite(led_1,HIGH);
    digitalWrite(led_2,HIGH);
    digitalWrite(led_3,LOW);
   }
   else if (temp_value>30) {
   digitalWrite(led_1,HIGH);
   digitalWrite(led_2,HIGH);
   digitalWrite(led_3,HIGH);
   }

  }



  void read_sensors(void){
  Serial.print("TEMP:");
  Serial.print(temp_value);
  Serial.print(",");
  Serial.print("LIGHT:");
  Serial.print(ldr_value);
  Serial.print(",");
  Serial.print("OBJECT:");
  Serial.println(object_detect);
  }


String read(){
  String word = "";
  while(Serial.available()){
    delay(10);
    char c = Serial.read();
    word += c;

  }
  return word;
}
