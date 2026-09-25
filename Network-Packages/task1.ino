#include <WiFi.h>

const char* ssid     = "Test_Server";
const char* password = "password";

String serverUrl  = "http://192.168.137.1";

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println();
  Serial.print("正在連接至 ");
  Serial.println(ssid);

  // 開始連接 Wi-Fi
  WiFi.begin(ssid, password);

  // 等待連接成功
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("Wi-Fi 連接成功！");
  Serial.print("ESP32 的 IP 地址是: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // 主程式
}