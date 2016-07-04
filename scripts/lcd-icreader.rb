# coding: utf-8

# IC balance checker  /  2013-2015 @Akkiesoft
#   Licence:
#     MIT License
#   references:
#     http://homepage3.nifty.com/slokar/pasori/libpafe-ruby.html
#     http://iccard.jennychan.at-ninja.jp/format

require 'wiringpi'
require "pasori"

# Please set 0 to gpio_light if LCD doesn't have the backlight.

# For Switch Science i2c miniLCD
#  https://www.switch-science.com/catalog/1405/
contrast = "0x5d"
gpio_light = 0

# For Strawberry Linux SB1602BW
#  https://strawberry-linux.com/catalog/items?code=27021
# contrast = "0x5e"
# gpio_light = 7

# Please set 0 to gpio_beep if if you don't have the buzzer.
gpio_beep=0

class Lcd
  OUTPUT = 1

  def initialize
    @io = WiringPi::GPIO.new
  end

  def setLcdInfo(i2cset, i2cbus, chip_addr, light_gpio=0, beep_gpio, contrast)
    @i2cset     = i2cset
    @i2cbus     = i2cbus
    @chip_addr  = chip_addr
    @light_gpio = light_gpio
    @beep_gpio  = beep_gpio
    @contrast   = contrast

    # if you are using Switch Science i2c miniLCD, comment out here.
    if @light_gpio != 0
      @io.pin_mode(@light_gpio, OUTPUT)
    end

    if @beep_gpio != 0
      @io.pin_mode(@beep_gpio, OUTPUT)
    end
  end

  def light(value)
    if @light_gpio != 0
      @io.digital_write(@light_gpio, value)
    end
  end

  def beep()
    if @beep_gpio != 0
      @io.digital_write(@beep_gpio, 1)
      sleep 0.1
      @io.digital_write(@beep_gpio, 0)
      sleep 0.025
      @io.digital_write(@beep_gpio, 1)
      sleep 0.1
      @io.digital_write(@beep_gpio, 0)
    end
  end

  def sendBlockData(v1, v2)
    `#{@i2cset} -y #{@i2cbus} #{@chip_addr} #{v1} #{v2} i`
  end

  def sendByteData(v1, v2)
    `#{@i2cset} -y #{@i2cbus} #{@chip_addr} #{v1} #{v2} b`
  end

  def reset
    sendBlockData(0, "0x38 0x39 0x14 0x78 " + @contrast + " 0x6c")
    sleep 0.25
    sendBlockData(0, "0x0c 0x01 0x06")
    sleep 0.05
  end

  def clear
    sendBlockData(0, 1)
  end

  def moveCursor(x, y)
    sendByteData(0, 128 + 64 * x + y)
  end

  def lcdprint(str)
    for x in str.split(//)
      sendstr = sendstr.to_s + " " + x.ord.to_s
    end
    sendBlockData(0x40, sendstr.to_s)
  end
end

def firstmessage(lcd)
  lcd.clear
  lcd.moveCursor(0,0)
  lcd.lcdprint("Please touch IC.")
end

lcd = Lcd.new
lcd.setLcdInfo("/usr/sbin/i2cset", 1, 0x3e, gpio_light, gpio_beep, contrast)

lcd.reset
lcd.clear
firstmessage(lcd)

pasori = Pasori.open

begin
  begin
    felica = pasori.felica_polling
    system = felica.request_system()
    card = {}
    system.each {|s|
      if (s == Felica::POLLING_SUICA || s == -31065 || s == -32546 || s == -31138 || s == -30261)
        # Suica (Generic traffic IC card) balance
        felica.foreach(Felica::SERVICE_SUICA_HISTORY) {|l|
          data = l.unpack('CCnnCCCCvN')
          card["name"] = "Suica"
          if (s == -32546)
            card["name"] = "Iruca" end
          if (s == -31138)
            card["name"] = "SAPICA" end
          if (s == -30261)
            # PASMO(TOKYU noruleage honorary station master card)
            card["name"] = "PASMO" end
          card["balance"] = data[8]
          break
        }
        # SAPICA point
        felica.foreach(0xBA4B) {|l|
          data = l.unpack('CCCNNNC')
          card["point"] = data[2] | data[1] | data[0]
        }
      elsif (s == -512)
        pasori.felica_polling(Felica::POLLING_EDY) {|felica2|
          # Edy balance
          felica2.foreach(0x1317) {|l|
            data = l.unpack('VVNnv')
            card["name"] = "Edy"
            card["balance"] = data[0]
            break
          }
          # nanaco balance
          felica2.foreach(0x5597) {|l|
            data = l.unpack('VVVV')
            card["name"] = "nanaco"
            card["balance"] = data[0]
            break
          }
          # nanaco point
          cnt = 0
          felica2.foreach(0x560B) {|l|
            if (cnt == 0)
              cnt += 1
              next
            end
            data = l.unpack('CCC')
            card["point"] = data[0] << 16 | data[1] << 8 | data[2]
            break
          }
          # waon balance
          felica2.foreach(0x6817) {|l|
            data = l.unpack('vNNNn')
            card["name"] = "waon"
            card["balance"] = data[0]
            break
          }
          # waon point
          felica2.foreach(0x684B) {|l|
            data = l.unpack('CCC')
            card["point"] = data[0] << 16 | data[1] << 8 | data[2]
            break
          }
        }
      elsif (s == -28735)
        pasori.felica_polling(Felica::POLLING_ANY) {|felica2|
          felica2.foreach(0x028F) {|l|
            data = l.unpack('nnnnnvnn')
            card["balance"] = data[5]
            card["name"] = "OKICA"
            break
          }
        }
      else
        if (s != 1223 && s != -32638 && s != -31445)
          card["name"] = "Unknown"
          card["balance"] = sprintf("%d(%X)", s, s)
        end
      end
    }
    lcd.light(1)
    lcd.clear
    lcd.moveCursor(0,0)
    if card["name"] == "Unknown"
      lcd.lcdprint("Unknown card.")
      lcd.moveCursor(1,0)
      lcd.lcdprint("#{card["balance"]}")
    else
      lcd.lcdprint("#{card["name"]} ｻﾞﾝﾀﾞｶ:".encode("Shift_JIS"))
      lcd.moveCursor(1,0)
      balance = sprintf("%c%s", 0x5c, card["balance"]).encode("Shift_JIS")
      if card["point"]
        balance += sprintf("/%spts", card["point"]).encode("Shift_JIS")
      end
      lcd.lcdprint(balance)
      lcd.beep()
    end
    sleep 5
    lcd.light(0)
    firstmessage(lcd)
  rescue => ee
    sleep 1
  end while true

rescue Interrupt
  lcd.clear()
  felica.close
  pasori.close
  print "\n\n"
  exit 0
end
