#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from get_icon import get_icon
from jptext import jptext

def print_receipt(printer, name, sn, icon, status):
  if (-1 < status.find(u"debug")):
      printer.set(align="left", text_type="NORMAL",width=1,height=1)
      printer.text("receive: ok\n")
  if (-1 < status.find(u"ニャーン")):
      printer.set(align="left", text_type="NORMAL",width=1,height=1)
      printer._raw(jptext("@" + sn + "\n" + status + "\n\n"))
  if (-1 < status.find(u"うすいほん")):
      printer.set(align="center", text_type="B",width=1,height=3)
      printer._raw(jptext(u"Ejectコマンドユーザー会\n同人誌をPDFで頒布中！！\n"))
      printer.set(align="center", text_type="NORMAL",width=1,height=1)
      printer.text("https://eject.booth.pm/\n\n")
      printer.text("\n\n")
      #printer.image("/home/pi/ejectboothpm2.png", False, True, 'bitImageColumn')
  if (-1 < status.find(u"ちらし")):
      printer.set(align="center", text_type="NORMAL",width=1,height=2)
      printer.text("Japanese Raspberry Pi\n Users Group\n")
      printer.set(align="left", text_type="NORMAL",width=1,height=1)
      printer.text("URL: http://raspi.jp/\n\n")
      printer.set(align="center", text_type="NORMAL",width=1,height=2)
      printer._raw(jptext(u"Ejectコマンドユーザー会\n"))
      printer.set(align="left", text_type="NORMAL",width=1,height=1)
      printer.text("URL: http://eject.kokuda.org/\n\n")
      printer.set(align="center", text_type="NORMAL",width=1,height=2)
      printer.text("@Akkiesoft Github\n")
      printer.set(align="center", text_type="NORMAL",width=1,height=1)
      printer.text("http://github.com/Akkiesoft/\n\n")
      printer.set(align="left", text_type="NORMAL",width=1,height=1)
      printer._raw(jptext(u"☆RPi-toolsリポジトリ:\n    便利なAnsible Playbook\n    展示物と同じスクリプトなど\n\n☆Eject-Command-Users-Group\n  リポジトリ\n    Ejectっぽいスクリプトとか\n\n\n\n"))
  if (-1 < status.find(u"なふだ")):
      get_icon(icon, "/tmp/icon_orig", "/tmp/icon_resize.png")
      printer.set(align="center", text_type="BU",width=3,height=3)
      printer.text("@" + sn + "\n")
      printer.set(align="center", text_type="NORMAL",width=1,height=1)
      printer._raw(jptext(name + "\n\n\n"))
      printer.image("/tmp/icon_resize.png", False, True, 'bitImageColumn')
      printer.set(align="center", text_type="normal",height=1)
      printer.text("\n\n\n\n")
