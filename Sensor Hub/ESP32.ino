//All the AirValues (known values are 2 and 3, all unknowns are shown as 100)
const int AirValue1 = 100;
const int AirValue2 = 3570;
const int AirValue3 = 3500;
const int AirValue4 = 100;
const int AirValue5 = 100;
const int AirValue6 = 100;

//All the WaterValues (known values are 2 and 3, all unknowns are shown as 0)
const int WaterValue1 = 0;
const int WaterValue2 = 1690;
const int WaterValue3 = 1640;
const int WaterValue4 = 0;
const int WaterValue5 = 0;
const int WaterValue6 = 0;

//All the soil moisture values
int soilMoistureValue1 = 0;
int soilMoistureValue2 = 0;
int soilMoistureValue3 = 0;
int soilMoistureValue4 = 0;
int soilMoistureValue5 = 0;
int soilMoistureValue6 = 0;

//All the soild moisture in percentage values
int soilmoisturepercent1 = 0;
int soilmoisturepercent2 = 0;
int soilmoisturepercent3 = 0;
int soilmoisturepercent4 = 0;
int soilmoisturepercent5 = 0;
int soilmoisturepercent6 = 0;

void setup() {
  Serial.begin(9600); // open serial port, set the baud rate to 9600 bps
}
void loop() {
  soilMoistureValue1 = analogRead(GPIO_NUM_36);
  soilMoistureValue2 = analogRead(GPIO_NUM_39);
  soilMoistureValue3 = analogRead(GPIO_NUM_32);
  soilMoistureValue4 = analogRead(GPIO_NUM_33);
  soilMoistureValue5 = analogRead(GPIO_NUM_34);
  soilMoistureValue6 = analogRead(GPIO_NUM_35);


  soilmoisturepercent1 = map(soilMoistureValue1, AirValue1, WaterValue1, 0, 100);
  soilmoisturepercent2 = map(soilMoistureValue2, AirValue2, WaterValue2, 0, 100);
  soilmoisturepercent3 = map(soilMoistureValue3, AirValue3, WaterValue3, 0, 100);
  soilmoisturepercent4 = map(soilMoistureValue4, AirValue4, WaterValue4, 0, 100);
  soilmoisturepercent5 = map(soilMoistureValue5, AirValue5, WaterValue5, 0, 100);
  soilmoisturepercent6 = map(soilMoistureValue6, AirValue6, WaterValue6, 0, 100);

  if (soilmoisturepercent1 > 10 && soilmoisturepercent1 < 90)
  {
    Serial.println("\n ADC0: ");
    Serial.print(soilMoistureValue1);
  }
  delay(250);

  if (soilmoisturepercent2 > 10 && soilmoisturepercent2 < 90)
  {
    Serial.println("\n ADC3: ");
    Serial.print(soilMoistureValue2);
  }
  delay(250);

  if (soilmoisturepercent3 > 10 && soilmoisturepercent3 < 90)
  {
    Serial.println("\n ADC4: ");
    Serial.print(soilMoistureValue3);
  }
  delay(250);

  if (soilmoisturepercent4 > 10 && soilmoisturepercent4 < 90)
  {
    Serial.println("\n ADC5: ");
    Serial.print(soilMoistureValue4);
  }
  delay(250);
  if (soilmoisturepercent5 > 10 && soilmoisturepercent5 < 90)
  {
    Serial.println("\n ADC6: ");
    Serial.print(soilMoistureValue5);
  }
  delay(250);

  if (soilmoisturepercent6 > 10 && soilmoisturepercent6 < 90)
  {
    Serial.println("\n ADC7: ");
    Serial.print(soilMoistureValue6);
  }
  delay(250);
}
