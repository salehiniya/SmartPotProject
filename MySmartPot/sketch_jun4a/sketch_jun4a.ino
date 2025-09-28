#include <LiquidCrystal.h>
#include <DHT.h>

#define DHTPIN 6
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

LiquidCrystal lcd(13, 12, 11, 10, 9, 8);

const int moisturePin = A0;
const int ledPin = 7;
const int tempAlertPin = 5;
const int lightPin = A1;
const int norPin = 4;

const int moistureThreshold = 300;
const int lightThreshold = 900;

unsigned long lastSwitchTime = 0;
bool showLight = false;

void setup() {

  Serial.begin(9600);

  pinMode(ledPin, OUTPUT);
  pinMode(tempAlertPin, OUTPUT);
  pinMode(norPin, OUTPUT);

  lcd.begin(16, 2);
  dht.begin();

  lcd.print("Smart Flowerpot");
  delay(1000);
  lcd.clear();

}

void loop() {
  int moistureValue = analogRead(moisturePin);
  int lightValue = analogRead(lightPin);
  float temp = dht.readTemperature();

  if (millis() - lastSwitchTime > 2000) {  // هر ۲ ثانیه تغییر کند
    showLight = !showLight;
    lastSwitchTime = millis();
    lcd.clear();
  }

  if (showLight) {
    // نمایش نور محیط
    lcd.setCursor(0, 0);
    lcd.print("Light: ");
    lcd.print(lightValue);
    if (lightValue > lightThreshold) {
      lcd.setCursor(0, 1);
      lcd.print("Harmful Light!");
     
    } else {
      lcd.setCursor(0, 1);
      lcd.print(" OK Light ");
    }
  } 
  
  else {
    // نمایش رطوبت و دما
    lcd.setCursor(0, 0);
    lcd.print("Moist: ");
    lcd.print(moistureValue);
    if (moistureValue < moistureThreshold) {
      lcd.print(" DRY ");
      digitalWrite(ledPin, HIGH);
    } else {
      lcd.print(" WET ");
      digitalWrite(ledPin, LOW);
    }

    lcd.setCursor(0, 1);
    if (isnan(temp)) {
      lcd.print("Temp Error");
    } else {
      lcd.print("Temp: ");
      lcd.print(temp, 1);
      lcd.print((char)223);
      lcd.print("C ");
      if (temp > 30) {
        lcd.print("HOT ");
        digitalWrite(tempAlertPin, HIGH);
      } else if (temp < 18) {
        lcd.print("COLD");
        digitalWrite(tempAlertPin, HIGH);
      } else {
        lcd.print("    ");
        digitalWrite(tempAlertPin, LOW);
      }
    }
  }

  // هشدار LED در صورت نور زیاد
  if (lightValue > lightThreshold) {
    digitalWrite(norPin, HIGH);
  } else {
    digitalWrite(norPin, LOW);
  }
   
 
      // ======== ارسال سریال به برنامه پایتون ========
  if (!isnan(temp)) {
    Serial.print(temp);
    Serial.print(",");
    Serial.print(lightValue);
    Serial.print(",");
    Serial.print(moistureValue);

    // اضافه کردن پیام‌های هشدار
    if (temp > 30) Serial.print(",HIGH_TEMP");
    else if (temp < 15) Serial.print(",LOW_TEMP");

    if (lightValue > 900) Serial.print(",HIGH_LIGHT");
    else if (lightValue < 200) Serial.print(",LOW_LIGHT");

    if (moistureValue > 800) Serial.print(",HIGH_MOISTURE");
    else if (moistureValue < 300) Serial.print(",LOW_MOISTURE");

    Serial.println();  // پایان خط
  }

 





  delay(200);  // تأخیر جزئی برای نرمی نمایش
}
