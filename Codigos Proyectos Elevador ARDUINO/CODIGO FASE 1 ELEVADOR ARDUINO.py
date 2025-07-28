#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <WiFi.h>
#include "time.h"
#include <ESP32Servo.h>

#define BOTON_P1 13
#define BOTON_P2 12
#define BOTON_P3 14

#define LED_VERDE 16
#define LED_AMARILLO 4
#define LED_ROJO 2

#define SERVO_PIN 27

#define FINAL_P1 26
#define FINAL_P3 25
#define SENSOR_IR 34

const char* ssid = "CLARO_GUACHAMIN"; 
const char* password = "RataDejadeRobar23"; 

LiquidCrystal_I2C lcd(0x27, 16, 2);

Servo servo;

int pisoActual = 1;
int pisoDestino = 0;
bool enMovimiento = false;
unsigned long ultimoCambioLed = 0;
bool estadoLed = false;
int ledDestino = 0;

unsigned long ultimoUpdateLCD = 0;
String mensajeAnterior = "";
unsigned long tiempoLlegada = 0;
bool mostrarLlegada = false;

void setupWiFi() {
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) delay(500);
  configTime(-5 * 3600, 0, "pool.ntp.org", "time.nist.gov");
}

String obtenerHora() {
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) return "No hora";
  char horaStr[16];
  strftime(horaStr, sizeof(horaStr), "%H:%M:%S", &timeinfo);
  return String(horaStr);
}

void actualizarPantalla(String mensaje) {
  String hora = obtenerHora();
  if (mensaje != mensajeAnterior || millis() - ultimoUpdateLCD > 1000) {
    lcd.setCursor(0, 0); 
    lcd.print("Hora: " + hora + "  ");  
    lcd.setCursor(0, 1); 
    lcd.print("                "); 
    lcd.setCursor(0, 1); 
    lcd.print(mensaje);
    mensajeAnterior = mensaje;
    ultimoUpdateLCD = millis();
  }
}

void moverAscensor(int destino) {
  if (destino == pisoActual || enMovimiento) return;
  pisoDestino = destino;
  enMovimiento = true;

  if (pisoDestino > pisoActual) {
    servo.write(180);  
    actualizarPantalla("Subiendo...");
  } else {
    servo.write(0);    
    actualizarPantalla("Bajando...");
  }
}

void detenerAscensor() {
  servo.write(90);  
  enMovimiento = false;
  pisoActual = pisoDestino;

  digitalWrite(LED_VERDE, pisoActual == 1);
  digitalWrite(LED_AMARILLO, pisoActual == 2);
  digitalWrite(LED_ROJO, pisoActual == 3);

  mostrarLlegada = true;
  tiempoLlegada = millis();

  actualizarPantalla("Llegada Piso " + String(pisoActual));
}

void setup() {
  Serial.begin(115200);

  pinMode(BOTON_P1, INPUT_PULLUP);
  pinMode(BOTON_P2, INPUT_PULLUP);
  pinMode(BOTON_P3, INPUT_PULLUP);

  pinMode(LED_VERDE, OUTPUT);
  pinMode(LED_AMARILLO, OUTPUT);
  pinMode(LED_ROJO, OUTPUT);

  pinMode(FINAL_P1, INPUT_PULLUP);
  pinMode(FINAL_P3, INPUT_PULLUP);
  pinMode(SENSOR_IR, INPUT);

  Wire.begin(21, 22);
  lcd.init(); 
  lcd.backlight();
  servo.attach(SERVO_PIN);

  setupWiFi();

  actualizarPantalla("Bienvenido");

  delay(2000); 

  
  if (digitalRead(FINAL_P1) == HIGH) {
    moverAscensor(1);
  } else {
    pisoActual = 1;
    digitalWrite(LED_VERDE, HIGH);
    actualizarPantalla("Piso actual: 1");
  }
}

void loop() {
  
  if (!digitalRead(BOTON_P1)) { pisoDestino = 1; ledDestino = LED_VERDE; moverAscensor(1); }
  if (!digitalRead(BOTON_P2)) { pisoDestino = 2; ledDestino = LED_AMARILLO; moverAscensor(2); }
  if (!digitalRead(BOTON_P3)) { pisoDestino = 3; ledDestino = LED_ROJO; moverAscensor(3); }

  if (enMovimiento && millis() - ultimoCambioLed >= 300) {
    estadoLed = !estadoLed;
    digitalWrite(ledDestino, estadoLed);
    ultimoCambioLed = millis();
  }

  if (enMovimiento) {
    if ((pisoDestino == 1 && digitalRead(FINAL_P1) == LOW) ||
        (pisoDestino == 3 && digitalRead(FINAL_P3) == LOW) ||
        (pisoDestino == 2 && analogRead(SENSOR_IR) < 2000)) {
      detenerAscensor();
    }
  }

  if (mostrarLlegada && millis() - tiempoLlegada >= 2000) {
    mostrarLlegada = false;
    actualizarPantalla("Piso actual: " + String(pisoActual));
  } else if (!enMovimiento && !mostrarLlegada) {
    actualizarPantalla("Piso actual: " + String(pisoActual));
  } else {
    actualizarPantalla(mensajeAnterior); 
  }
}