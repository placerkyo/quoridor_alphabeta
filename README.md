# アルファベータ法によるコリドールの自動対戦プログラム

このリポジトリは，学部3年次に「ソフトウェア実験」という講義において作成した二人対戦ゲーム「コリドール」の自動対戦プログラムと発表資料が入っている．

## ファイルの説明
- make_player.py : 作成した自動対戦プログラム．盤面情報を受け取り，次の手を返す．
- 発表資料.pptx : 講義で用いた最終発表資料．工夫点を記載している．
- 最終レポート.pdf : 講義の最後に提出したレポート．作成したプログラムについての詳細を記載している．

## 工夫点

自動対戦プログラムを作成するうえで，行った工夫を簡単に述べる．

### 1. アルファベータ法による先読み

探索アルゴリズムであるアルファベータ法を用いて3手先まで読み，最も良いと考えられる手を探索できるようにした．ミニマックス法ではなくアルファベータ法を用いることで，探索にかかる時間を削減した．

### 2. 評価関数の重みの学習

最も良い手を見つけるためには，見つける基準となる評価関数を正しく設定する必要がある．評価関数を計算するうえで以下の点を考慮することにした．

- 自分のゴールまでの最短距離
- 相手のゴールまでの最短距離
- 残壁の数

これらをパラメータとして，PA（Passive Aggressive）という線形分類器で二値分類の学習を行い、重さを決定した．すなわち，上のパラメータをどれほど重視すればよいかを学習した．

学習データには自己対戦して得られるデータを用いた．4回自己対戦を行い，学習し，重みを更新し次の自己対戦を行うことで学習を行う．

### 3. 実行時間の短縮
実行時間の短縮のために，以下の工夫を行った．
- 幅優先探索と深さ優先探索の使い分け
- 評価値の高い手のみ先読み



## 実行方法
作成したmake_player同士を対戦させるには、以下のようにサーバーコマンドを実行する。
```
python3 server.py -1 make_player.py -2 make_player.py
```
ただし，server.pyは講義で配布されるプログラムであり，このリポジトリには入っていない．

　