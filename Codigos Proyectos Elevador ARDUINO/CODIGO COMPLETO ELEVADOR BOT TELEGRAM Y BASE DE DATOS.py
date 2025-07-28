#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <WiFi.h>
#include "time.h"
#include <ESP32Servo.h>
#include <WiFiClientSecure.h>
#include <UniversalTelegramBot.h>
#include <HTTPClient.h>

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

#define BOT_TOKEN "8096110246:AAErkxbUfQ2UDGCGp2Q_2BzuATYEW56kpU0"
#define CHAT_ID ""
WiFiClientSecure secured_client;
UniversalTelegramBot bot(BOT_TOKEN, secured_client);
bool serialConectado = true;
bool yaRedirigido = false;

LiquidCrystal_I2C lcd(0x27, 16, 2);

Servo servo;

int pisoActual = 1;
int pisoDestino = 0;
bool enMovimiento = false;
unsigned long ultimoCambioLed = 0;
bool estadoLed = false;
int ledDestino = 0;

bool activacionTelegram = false;

unsigned long ultimoUpdateLCD = 0;
String mensajeAnterior = "";
unsigned long tiempoLlegada = 0;
bool mostrarLlegada = false;

void enviarRegistroAlServidor(int piso, String tipoActivacion) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin("http://192.168.100.34:5000/registro");  
    http.addHeader("Content-Type", "application/json");

    String horaActual = obtenerHora();  
    String json = "{\"piso\":" + String(piso) + 
                  ",\"hora\":\"" + horaActual + 
                  "\",\"tipo\":\"" + tipoActivacion + "\"}";

    int httpResponseCode = http.POST(json);
    http.end();
  }
}

void setupWiFi() {
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) delay(500);
  configTime(-5 * 3600, 0, "pool.ntp.org", "time.nist.gov");

  
  struct tm timeinfo;
  while (!getLocalTime(&timeinfo)) {
    Serial.println("Esperando NTP...");
    delay(1000);
  }
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

void enviarEstadoTelegram(String estado) {
  bot.sendMessage(CHAT_ID, estado, "");
}

void moverAscensor(int destino, bool esTelegram) {
  if (destino == pisoActual || enMovimiento) return;
  pisoDestino = destino;
  enMovimiento = true;
  activacionTelegram = esTelegram;

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
  
  String tipo = (activacionTelegram) ? "telegram" : "boton";  
  enviarRegistroAlServidor(pisoActual, tipo);
}

void handleTelegram() {
  static unsigned long lastBotCheck = 0;
  if (millis() - lastBotCheck < 2000) return;
  lastBotCheck = millis();

  int numNewMessages = bot.getUpdates(bot.last_message_received + 1);
  while (numNewMessages) {
    for (int i = 0; i < numNewMessages; i++) {
      String msg = bot.messages[i].text;
      String chat_id = bot.messages[i].chat_id;
      String reply;

      if (CHAT_ID == "") {
        enviarEstadoTelegram("Bot enlazado con este chat");
      }

      if (msg == "/start") {
        reply = "Bienvenido al Parqueadero del Edificio Maze Bank\nActualmente en el Piso " + String(pisoActual) + ".\nDesea ir a otro piso:\n/Piso1\n/Piso2\n/Piso3";
      } else if (msg == "/Piso1" || msg == "/piso1") {
        if (pisoActual == 1) reply = "Actualmente ya está en el Piso 1.";
        else {
          moverAscensor(1, true);  
          reply = "Redirigiendo al Piso 1...";
        }
      } else if (msg == "/Piso2" || msg == "/piso2") {
        if (pisoActual == 2) reply = "Actualmente ya está en el Piso 2.";
        else {
          moverAscensor(2, true);
          reply = "Subiendo al Piso 2...";
        }
      } else if (msg == "/Piso3" || msg == "/piso3") {
        if (pisoActual == 3) reply = "Actualmente ya está en el Piso 3.";
        else {
          moverAscensor(3, true);
          reply = "Subiendo al Piso 3...";
        }
      } else {
        reply = "Comando no reconocido. Usa /Piso1, /Piso2, /Piso3";
      }

      bot.sendMessage(chat_id, reply, "");
    }

    numNewMessages = bot.getUpdates(bot.last_message_received + 1);
  }
}

void tareaTelegram(void *parameter) {
  while (true) {
    handleTelegram();
    vTaskDelay(2000 / portTICK_PERIOD_MS);
  }
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

  secured_client.setInsecure();
  setupWiFi();

  actualizarPantalla("Bienvenido");
  delay(2000);

  if (digitalRead(FINAL_P1) == HIGH) {
    moverAscensor(1, false);
    actualizarPantalla("Redirigiendo al P1");
    enviarEstadoTelegram("Redirigiendo al Piso 1...");
  } else {
    pisoActual = 1;
    digitalWrite(LED_VERDE, HIGH);
    actualizarPantalla("Piso actual: 1");
    enviarEstadoTelegram("Bienvenido al Parqueadero del Edificio Maze Bank\nActualmente en el Piso 1.\nDesea ir a otro piso:\n/Piso2\n/Piso3");
  }

  xTaskCreate(
    tareaTelegram,
    "TareaTelegram",
    8192,
    NULL,
    1,
    NULL
  );
}

void loop() {
  if (!digitalRead(BOTON_P1)) { moverAscensor(1, false); ledDestino = LED_VERDE; }
  if (!digitalRead(BOTON_P2)) { moverAscensor(2, false); ledDestino = LED_AMARILLO; }
  if (!digitalRead(BOTON_P3)) { moverAscensor(3, false); ledDestino = LED_ROJO; }

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

  if (!Serial && serialConectado) {
    serialConectado = false;
    if (pisoActual != 1 && !yaRedirigido) {
      actualizarPantalla("Redirigiendo al P1");
      moverAscensor(1, false);
      enviarEstadoTelegram("Redirigiendo al Piso 1...");
      yaRedirigido = true;
    }
  }

  if (!Serial && pisoActual == 1 && !serialConectado && yaRedirigido) {
    enviarEstadoTelegram("Bienvenido al Parqueadero del Edificio Maze Bank\nActualmente en el Piso 1.\nDesea ir a otro piso:\n/Piso2\n/Piso3");
    yaRedirigido = false;
  }
}
