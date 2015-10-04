# Raspberry Pi向けのいろいろ使える感じのツール

ちょっとしたツールとかそういうのをためておくところ。おもにAnsible playbook。

## Ansible playbook

Raspberry Piの各種環境構築に役立つかもしれないPlaybookをまとめたものである。Ansible バージョン1.9.2で動作を確認済み。

### Role 一覧

| role名 | 内容 | 依存するRole | varsの有無 |
| --- | --- |
| jessie | Wheezy環境にJessieのリポジトリを追加する | なし |
| lcd-icreader | SB1602系などのI2C通信のLCDモジュールを使ってRC-S320でICカードの残高を表示する環境を構築する | なし |
| mikutter | mikutterをインストールする | jessie, ruby2.1 | なし |
| mt7650u | GW-450Dなどmt7650uチップのWi-Fiドライバをインストールする（ドライバーバイナリは別途用意が必要） | なし |
| rpi-source | ドライバーやカーネルコンパイル用の環境を構築する | なし |
| ruby2.1 | Ruby 2.1をインストールする | jessie | なし |
| wifi | NetworkManagerの導入およびWi-Fi設定 | あり |

### vars

#### wifi role用のvars

Wi-fiの接続設定は、複数記述が可能。varsの内容は、host_vars以下に配置しておくと楽。

```
wifi:
  - type: wpa-pskもしくはwep
    ssid: SSID名
    pass: パスフレーズ
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
