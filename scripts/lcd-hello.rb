#!/usr/bin/env ruby
# coding: utf-8

require 'wiringpi'

# Please set 0 to gpio_light if LCD doesn't have the backlight.

# For Switch Science i2c miniLCD
#  https://www.switch-science.com/catalog/1405/
contrast = 0x5d
gpio_light = 0

# For Strawberry Linux SB1602BW
#  https://strawberry-linux.com/catalog/items?code=27021
# contrast = 0x5e
# gpio_light = 7

class Lcd
  OUTPUT = 1

  def initialize(chip_addr, contrast, light_gpio=0)
    @chip_addr  = chip_addr
    @contrast   = contrast
    @light_gpio = light_gpio

    @io = WiringPi::GPIO.new
    @i2c = WiringPi::I2C.new(@chip_addr)

    if @light_gpio != 0
      @io.pin_mode(@light_gpio, OUTPUT)
    end
  end

  def sendBlockData(reg, block)
    block.each { |i| sendByteData(reg, i) }
  end

  def sendByteData(reg, byte)
    @i2c.write_reg_8(reg, byte)
  end

  def reset
    sendBlockData(0, [0x38, 0x39, 0x14, 0x78, @contrast, 0x6c])
    sleep 0.25
    sendBlockData(0, [0x0c, 0x01, 0x06])
    sleep 0.05
  end

  def set_contrast(contrast)
    @contrast = contrast
    reset
  end

  def clear
    sendBlockData(0, [1])
  end

  def moveCursor(x, y)
    sendByteData(0, 128 + 64 * y + x)
  end

  def lcdprint(str)
    for x in str.split(//)
      sendByteData(0x40, x.ord)
    end
  end

  def light(value)
    if @light_gpio != 0
      @io.digital_write(@light_gpio, value)
    end
  end
end

lcd = Lcd.new(0x3e, contrast, gpio_light)

lcd.reset
lcd.clear
lcd.moveCursor(0,0)
lcd.lcdprint("Hello!")
lcd.moveCursor(2,1)
lcd.lcdprint("World!")

