
2015-01-13
tag: ex1
ターン数制限付きでランダムAI同士の対戦
最大ターン数100回でランダム同士で1000回対戦させた結果:

Counter({'LOSE': 377, 'WIN': 376, 'EVEN': 247})
python t.py  0.00s user 6.45s system 99% cpu 6.465 total

最大ターン数300回の場合
Counter({'WIN': 509, 'LOSE': 490, 'EVEN': 1})
python t.py  0.00s user 7.23s system 99% cpu 7.252 total


tag: ex2
適当な実装の、ゴールをまっしぐらに目指すAI
print Counter(match(Random(), Fastest()) for x in range(1000))
print Counter(match(Fastest(), Random()) for x in range(1000))
print Counter(match(Fastest(), Fastest()) for x in range(1000))

Counter({'LOSE': 979, 'WIN': 21})
Counter({'WIN': 979, 'LOSE': 21})
Counter({'WIN': 646, 'LOSE': 354})
python t.py  0.00s user 9.04s system 99% cpu 9.075 total


tag: ex3
print Counter(match(Fastest(), FastestP(p=0.1)) for x in range(1000))
print Counter(match(FastestP(p=0.1), Fastest()) for x in range(1000))

Counter({'WIN': 688, 'LOSE': 312})
Counter({'WIN': 516, 'LOSE': 484})
python t.py  0.00s user 6.72s system 99% cpu 6.755 total

確率pでランダムに振る舞うFastestは、Fastest相手だとpの増加とともに勝率が下がる。
当たり前、Fastestは相手の色の推定をしていないから。

相手の色の推定をして青を選んで取ってくるAIが相手だと弱くなるはず。
それに対してpが幾らかのところでピークを示すはず。
それが示せるといいな。

でもその前にFastestが知り得ない「この行動をしたら勝てるかどうか」を使っていたので
今後うっかりでそういうことが起こらないように、ゲームの情報を持つオブジェクトと、
個別のAIに渡される、そのAIから見える情報だけのオブジェクトを分離する作業をしたい。

-----
次のアクション
色を推定して取るAI
Fastestとの強さの比較、pの値を変えて調査

tag:ex4
相手の動作を見て、隠された情報を推定する

1 0.420040899796
2 0.444171779141
3 0.440081799591
4 0.428220858896
7 1.0
8 0.420858895706
9 0.434355828221
10 0.41226993865
.vvvv.
v.vvv.
......
......
.xoox.
.xoox.

python t.py  0.00s user 3.93s system 99% cpu 3.955 total
1万回のランダムな隠れ状態作成→相手のモデルで1手打つ
→その手が一致しているものだけを選ぶ（ここまで、要するに棄却サンプリング）
で推定した。4秒。そこまで掛けなくても良いとは思う。

1000回でやったものがこちら
1 0.464730290456
2 0.44398340249
3 0.464730290456
4 0.390041493776
7 1.0
8 0.419087136929
9 0.423236514523
10 0.394190871369

-----

2015-02-02

モンテカルロで手を選ぶAIを実装する
そしてそれのランダムに対する勝率を調べる

各手10回のランダムプレイアウトで一番成績の良かったものを選ぶやつで
1回対戦するのに掛かる時間：4分

高速化が必要。
ボトルネックはmallocなのでBoostPythonが必要か



2017-01-07

仕切り直し。

とりあえず現状を確認。プロファイラなしで起動

$ time python ex1.py
Counter({'WIN': 1})
python ex1.py  54.45s user 0.17s system 97% cpu 55.960 total

プロファイラありで起動。

$ time kernprof -l ex1.py
Counter({'WIN': 1})
Wrote profile results to ex1.py.lprof
kernprof -l ex1.py  252.32s user 46.21s system 99% cpu 5:01.20 total

profile.txtに結果を保存。2年前はボトルネックはmallocって書いてるけど、
random_playoutから呼ばれてるdo_moveとrandom.choiceが大きい。
do_moveの中ではgame.get_rotatedとgame.set_valが50%を占めていて、
とりあえずmeとopをタプルにしたり戻したりしている所や、長さ8のリストをコピーしているところが無駄っぽいので削ってみよう。


2017-01-14

https://github.com/miyo/geister_server.java の新しいプロトコルで動くように修正。

2017-08-10
Tiny(4x4のボード)で
各々の手を10回ランダムプレイアウトして最良の手を選ぶモンテカルロで
モンテカルロvsランダムを100回やった場合
所要時間13秒で、モンテカルロの勝率7割
Counter({'WIN': 71, 'LOSE': 29})
12.52791

先手後手交換しても同じ
Counter({'LOSE': 71, 'WIN': 29})

両方モンテカルロの場合、所要時間50秒で、若干先手が有利
Counter({'WIN': 52, 'LOSE': 48})
49.07341

