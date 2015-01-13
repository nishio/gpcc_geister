
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

