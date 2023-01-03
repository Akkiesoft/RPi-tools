# E220-900T22S(JP)向けのスクリプト

LoRaモジュール「E220-900T22S(JP)」用のスクリプト各種です。

## mode.py

モード設定を変更したり確認したりできるスクリプトです。RPi.GPIOモジュールを使用しますが、Raspberry Pi OSにバンドルされているため、ライブラリの導入は不要です。

* 確認
  ```
  python3 mode.py
  ```
* 設定
  ```
  python3 mode.py <0-3>
  ```

## circuitpython/receive.py

メーカーの受信サンプルスクリプトをCircuitPythonに移植して、さらにOLEDで受信内容を表示できるようにしたスクリプトです。