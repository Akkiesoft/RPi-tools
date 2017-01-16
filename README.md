# Raspberry Pi向けのいろいろ使える感じのツール

ちょっとしたツールとかそういうのをためておくところ。おもにAnsible playbook。

## Ansible playbook

Raspberry Piの各種環境構築に役立つかもしれないPlaybookをまとめたものである。Ansible バージョン1.9系で動作するとおもう。

### Role 一覧

| role名 | 内容 | 依存するRole | varsの有無 |
| --- | --- | --- | --- |
| jessie | Wheezy環境にJessieのリポジトリを追加する | なし | なし |
| l-05a | NetworkManagerでL-05Aを使用してモバイル接続する | network-manager | あり |
| fuckinhotmon | DS18B20もしくはZabbixから取得する室温をNokia5110LCDで表示する環境を構築する | なし | あり |
| lcd-icreader | SB1602系などのI2C通信のLCDモジュールを使ってRC-S320でICカードの残高を表示する環境を構築する | なし | なし |
| mikutter | mikutterをインストールする | jessie, ruby2.1 | なし |
| mt7650u | GW-450Dなどmt7650uチップのWi-Fiドライバをインストールする（ドライバーバイナリは別途用意が必要） | なし | なし |
| network-manager | NetworkManagerを導入する | なし | なし | 
| rpi-source | ドライバーやカーネルコンパイル用の環境を構築する | なし | なし |
| rtl8192cu | rtl8192cuドライバーの省電力オプションを無効化する | なし | なし |
| ruby2.1 | Ruby 2.1をインストールする | jessie | なし |
| timelapse-camera | タイムラプスカメラ環境を作る | なし | なし |
| wifi | NetworkManager用のWi-Fi設定ファイルを投入する | network-manager | あり |

### vars

#### wifi role用のvars

Wi-fiの接続設定は、複数記述が可能。varsの内容は、host_vars以下に配置しておくと楽。

```
wifi:
  - type: wpa-pskもしくはwep
    ssid: SSID名
    pass: パスフレーズ
```

#### l-05a role用のvars

複数記述が可能。

```
mobile_network:
  - name: NetworkManagerの接続名
    number: 接続先の番号
    username: ユーザー名
    password: パスワード
    apn: APN
```

#### fuckinhotmon role用のvars

```
# Local Temperature
use_ds18b20: yes|no (DS18B20センサーの値を出すかどうか)
ds18b20_id: 28-000000000000 (センサーのデバイスID)

# Configure below lines if override gpio port.
# http://akkiesoft.hatenablog.jp/entry/20150722/1437561722
ds18b20_override_gpio: yes|no (1-WireのGPIOピンをデフォルトの4番から変更するときに使用)
ds18b20_gpio_data: 26 (ds18b20_override_gpioをyesにした時、1-Wire用にしたいピン番号を指定)
ds18b20_gpio_vcc: 19 (ds18b20_override_gpioをyesにした時、常時通電するピンを指定可能)

# Zabbix Option
use_zabbix:  yes|no (Zabbixの室温アイテムを取得するかどうか)
zabbix_url: http://192.168.0.100/zabbix (ZabbixのURL)
zabbix_user: fuckinhot (Zabbixのユーザー名)
zabbix_pass: fuckinhot (Zabbixのパスワード)
zabbix_item_id: 12345 (アイテムID)

# threshould
threshold:
  hot: 30 (この室温以上になったら暑い時用の画像に切り替える)
  cold: 20 (この室温を下回ったら寒い時用の画像に切り替える)
```

#### timelapse-camera role用のvars

```
host: example.com (撮影した写真をSCPでアップロードするホスト)
port: 22 (撮影した写真をSCPでアップロードするホストのポート)
user: user (撮影した写真をSCPでアップロードするホストのユーザー)
private_key_path: /home/pi/.ssh/id_rsa (SSH接続するときの秘密鍵)
photo_file: /home/pi/photo.jpg (撮影した写真を保存するパス)
count_file: /home/pi/count.dat (カウントファイルのパス)
remote_path: /var/www/html/data (撮影した写真をSCPでアップロードする先のディレクトリ)
remote_count_path: /var/www/html/count.dat (カウントファイルのSCPアップロード先パス)
```

### hosts

基本的に[all]以下にホスト名をためておいて、-lオプションで絞り込むのが楽だと思う。また、ユーザーはあらかじめ書いておくと楽。

```
[all]
raspi1 ANSIBLE_SSH_USER=pi
raspi2 ANSIBLE_SSH_USER=pi
raspi3 ANSIBLE_SSH_USER=pi
```

### Roleの組み合わせ

Roleは自由に組み合わせて使用できる。依存するRoleに注意したうえで、Role一覧から選択をしていく。以下はmikutter環境を構築しつつ、Wi-Fiを設定するための組み合わせ。

mikutter.yml
```
---
- hosts: all
  roles:
  - jessie
  - ruby2.1
  - mikutter
  - wifi
```

### 実行

実行例を以下に示す。

```
mypc:ansible user$ ansible-playbook -i hosts -l raspi1 mikutter.yml 
```
