from guizero import App, Box, Text, Picture
import io
import urllib.request
from PIL import Image
import time
from zabbix.api import ZabbixAPI
import json

zbx = {
  'url': '',
  'user': '',
  'pass': ''
}
ohayo_list_url = 'https://kokuda.org/portal/json/ohayo.php'
ohayo_url = ""

def oha_text(t, l):
    return Text(textbox, text=t, grid=[0,l], align="left", size=24, font="Major Mono Display")

def update_time():
    clock.value = time.strftime("%Y/%m/%d %H:%M")

def update_pressure():
    t = z.item.get(itemids=25056)
    p = round(float(t[0]["lastvalue"]), 2)
    pressure.value = "%s hpa" % p

def update_ohayo():
    global ohayo_url
    ohayo_list = json.loads(urllib.request.urlopen(ohayo_list_url).read())
    if ohayo_url != ohayo_list[0]["image"]:
        ohayo_url = ohayo_list[0]["image"]
        data = io.BytesIO(urllib.request.urlopen(ohayo_url).read())
        img = Image.open(data)
        (ox,oy) = img.size
        ix = app.width + 2
        iy = int(oy * ix / ox)
        ohayo.value = img.resize((ix,iy), Image.LANCZOS)

def hide_show_textbox():
    textbox.visible = not textbox.visible

try:
  z = ZabbixAPI(url=zbx['url'], user=zbx['user'], password=zbx['pass'])
except:
  print('error.')
  sys.exit(1)

app = App(title="Ohayo signage")
app.full_screen = True
app.bg = "black"
app.text_color = "white"

textbox = Box(app, width="fill", height="fill", layout="grid")
clock = oha_text("", 1)
clock.repeat(1000, update_time)
pressure = oha_text("", 2)
pressure.repeat(60000, update_pressure)
ohayo = Picture(app)
ohayo.repeat(3600000, update_ohayo)
update_pressure()
update_ohayo()

ohayo.when_clicked = hide_show_textbox

app.display()
