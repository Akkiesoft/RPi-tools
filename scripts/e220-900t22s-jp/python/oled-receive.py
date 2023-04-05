import serial
import time
import argparse
import Adafruit_SSD1306
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# ディスプレイの初期化
disp = Adafruit_SSD1306.SSD1306_128_64(rst=None)
disp.begin()
disp.clear()
disp.display()
width = disp.width
height = disp.height

# PILのイメージを作成
image = Image.new('1', (width, height))

# PILイメージに描画
draw = ImageDraw.Draw(image)
fpath = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
font = ImageFont.truetype(fpath, 10)



def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("serial_port")
    parser.add_argument("-b", "--baud", default="9600")
    parser.add_argument("-m", "--model", default="E220-900JP")
    parser.add_argument("--rssi", action="store_true")

    args = parser.parse_args()

    return args


def main():
    args = get_args()

    if args.model == "E220-900JP":
        print("serial port:")
        print(args.serial_port)

        print("receive waiting...")
        ser = serial.Serial(args.serial_port, int(args.baud), timeout=None)
        payload = bytes()
        try:
            while True:
                now = time.strftime("%H:%M:%S")
                draw.rectangle((0,45,127,63), outline=0, fill=0)
                if ser.in_waiting != 0:
                    payload = payload + ser.read()
                elif ser.in_waiting == 0 and len(payload) != 0:
                    draw.rectangle((0,0,127,63), outline=0, fill=0)
                    time.sleep(0.010)
                    if ser.in_waiting == 0:
                        draw.text((0,0), "DATA: %s"%payload, font=font, fill=255)
                        #hexdump.hexdump(payload)
                        if args.rssi:
                            rssi = int(payload[-1]) - 256
                            draw.text((0,15), f"RSSI: {rssi} dBm", font=font, fill=255)
                            draw.text((0,30), f"RECV: {now}", font=font, fill=255)
                        payload = bytes()
                draw.text((0,45), "NOW: %s"%now, font=font, fill=255)
                disp.image(image)
                disp.display()
        except KeyboardInterrupt:
            ser.close()
        finally:
            ser.close()
    else:
        print("INVALID")
        return


if __name__ == "__main__":
    main()
