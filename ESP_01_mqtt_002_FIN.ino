/* Subscribe il topic: Led/bassa e Led/alta [0/1] mqtt 
 * sul broker Debian (192.168.1.20) OR (iot.eclipse.org)
 * [Attualmente Switch su un solo PIN ON=1 OFF=0 su tensione 220] 
 * Usa un ESP8266 mod.01 su PIN GPIO02
 * 
 * L'attuatore ESP STACCA lo SWITCH dopo un tempo T (regolabile) ora 6 minuti
 * Sia che si interrompa internet 
 * Sia che se si interrompa il Broker
 * per evitare LOOP infiniti con SWITCH in ON
 * 
 * VERSIONE con LIB. MQTTClient
 * Con broker remoto eclipse
 */


// Librerie usate
  #include <ESP8266WiFi.h>                                                                                                                                                                                          
  #include <MQTTClient.h>
  
// Pin a cui e connesso lo Switch 
  #define PinSWbassa 2  // Unico PIN usato per lo SWITCH
  #define PinSWalta 0
// Tempo dopo il quale lo SWITCH viene spento
  #define Time_off 240000  // millesec
// Attivazione delle stampe di controllo TEST=1
  #define Test 0
// inverte LED se in programmazione (porre a 0 quando installi SWITCH)
  #define Prog 1
// Dati di Connessione al broker locale
  //#define Broker_mio "192.168.1.20"
  //#define Port 1883
  #define Broker_mio "iot.eclipse.org"
  #define Port 1883
// credenziali per l'access point locale
//  const char* ssid     = "TP-LINK_B1BDFC";
//  const char* pass = "33757858";
  const char* ssid     = "Telecom-55159155";
  const char* pass = "giovannicupini15101949gc";
// creazione dell'oggetto broker mqtt
  const char* mqtt_server = Broker_mio;

WiFiClient espClient;
MQTTClient client;

unsigned long lastMillis = 0;

void connect(); // <- predefine connect() for setup()

void setup() {
  if (Test) Serial.begin(115200);
  // setting del pin di SWITCH
  pinMode(PinSWbassa,OUTPUT);
  if (Prog) digitalWrite(PinSWbassa,LOW);
  else digitalWrite(PinSWbassa,HIGH);
   pinMode(PinSWalta,OUTPUT);
  if (Prog) digitalWrite(PinSWalta,LOW);
  else digitalWrite(PinSWalta,HIGH);
  client.begin(Broker_mio, espClient);
  WiFi.begin(ssid, pass);
  if (Test) Serial.print("Verifica wifi...");
  while (WiFi.status() != WL_CONNECTED) {
    if (Test) Serial.print(".");
    delay(500);
  }
  connect();
}

void connect() {
  if (Test) Serial.print("\t...tentativo di connessione...");
  while (!client.connect("Arduino|ESP", "try", "try")) {
    if (millis()>Time_off) ESP.restart(); 
    if (Test) Serial.print(".");
    delay(1000);
  }
  if (Test)Serial.println("\n..Connesso..!");
  client.subscribe("Led/#");
  client.publish("Rileggi","1");
}

void loop() {
  if (millis()>Time_off) {
    ESP.restart(); 
  }
  if (!client.connected()) {
    connect();
  }else {
    client.loop();
    delay(500);
  }
}

void messageReceived(String topic, String payload, char * bytes, unsigned int length) {
  bool VAL;
  if (Prog) VAL=(bool) payload.toInt();
  else VAL=!(bool) payload.toInt();
  if (topic=="Led/bassa")  digitalWrite(PinSWbassa,VAL);
  if (topic=="Led/alta")  digitalWrite(PinSWalta,VAL);
  if (Test) {
    Serial.print("Topic: ");
    Serial.print(topic);
    Serial.print(" - ");
    Serial.print(payload);
    Serial.print(" - ");
    Serial.print(VAL);
    Serial.println();
  }
}
