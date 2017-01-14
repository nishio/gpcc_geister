# gpcc_geister

ガイスター関連のプログラムを雑においておくリポジトリです



## client.py

三好さんのガイスターサーバに接続できるPython版クライアントです。

https://github.com/miyo/geister_server.java

### 人間との対戦

オプションなしで起動すると、三好さんのHumanGUIPlayerを起動してPython製のDefaultAIと対戦できます。

### ランダムテスト
```
python -mpdb client.py --random-test --endless --ai=FooBarAI
```

FooBarAIとランダムAIを先手後手交代しながらプレイさせ続け、エラーが起きたらpdbでデバッグします。
実装したAIにバグがないことを確認するためのランダムテスト用のオプション群です。
