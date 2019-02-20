#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Thanks:
#   https://github.com/SIGCOWW/saty (printing Japanese)

def jptext(str):
  # 文字列を1文字ずつ読んで、マルチバイト文字をESCPOSで使える
  # エスケープコードなしのJIS文字に変換する
  output = []
  jpmode = 0
  jpstart = b'\x1c\x26'
  jpend   = b'\x1c\x2e'
  for c in str:
    c_jis = c.encode('iso2022_jp', 'ignore')
    # single byte code
    if len(c_jis) == 1:
      if jpmode:
        # end japanese mode
        jpmode = 0
        output.append(jpend)
      output.append(c_jis)
      continue
    # start japanese mode
    if not jpmode:
      jpmode = 1
      output.append(jpstart)
    # add multibytes character without escape code.
    output.append(c_jis[3:-3])
  # end japanese mode
  if jpmode:
    output.append(jpend)
  return b''.join(output)
