import SimpleHTTPServer
import SocketServer
from time import sleep
from Adafruit_CCS811 import Adafruit_CCS811
import threading

ccs = Adafruit_CCS811()
while not ccs.available():
	pass
temp = ccs.calculateTemperature()
ccs.tempOffset = temp - 25.0

ppm = 0
tvoc = 0

def co2_loop():
  global temp, ppm, tvoc
  while(1):
    if not running:
      break
    try:
      if ccs.available():
        temp = round(ccs.calculateTemperature(), 2)
      if not ccs.readData():
        ppm = ccs.geteCO2()
        tvoc = ccs.getTVOC()
      else:
        print("ERROR!")
    except:
      print("ERROR!")
    sleep(2)

PAGE=u"""\
<html lang="en">
<head>
<meta charset="utf-8">
<title>CCS811 CO2 sensor</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<script>
function updateCO2() {
var co2 = document.getElementById('co2');
fetch('/json').then(function(response){
  return response.json();
}).then(function(json){
  temp.innerHTML = json.temp;
  co2.innerHTML = json.co2;
  tvoc.innerHTML = json.tvoc;
  setTimeout(updateCO2, 5000);
});
}
window.onload = function() {
  updateCO2();
}
</script>
</head>
<body>
<h1>CCS811 CO2 Sensor</h1>
<p>
  Temperature: <span id="temp"></span> C<br>
  CO2: <span id="co2"></span> ppm<br>
  TVOC: <span id="tvoc"></span> ppb
</p>
<p>
API:
<a href="/json">JSON</a>,
Plain text(
<a href="/temp">Temperature</a>,
<a href="/co2">CO2</a>,
<a href="/tvoc">TVOC</a>
)
</p>
</body>
</html>
"""

class HttpHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def returnvalue(self, value, mime):
        s = str(value)
        content = PAGE.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', len(s))
        self.end_headers()
        self.wfile.write(s)

    def do_GET(self):
        global temp, ppm ,tvoc
        if self.path == '/':
            self.returnvalue(PAGE, "text/html")
        if self.path == '/json':
            json = '{"temp":' + str(temp) + ',"co2":' + str(ppm) + ',"tvoc":' + str(tvoc) + '}'
            self.returnvalue(json, "application/json")
        if self.path == '/temp':
            self.returnvalue(temp, "text/plain")
        if self.path == '/co2':
            self.returnvalue(ppm, "text/plain")
        if self.path == '/tvoc':
            self.returnvalue(tvoc, "text/plain")

try:
  running = True
  co2_thread = threading.Thread(target=co2_loop)
  co2_thread.start()

  address = ('', 8000)
  server = SocketServer.TCPServer(address, HttpHandler)
  server.serve_forever()
except KeyboardInterrupt:
  running = False

