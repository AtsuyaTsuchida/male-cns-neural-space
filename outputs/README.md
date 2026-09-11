# male-cnsを使った最小学習実験

## 結果

male-cns:v1.0の実接続を初期重みに使い、仮想刺激と報酬の対応を学ぶ簡略モデルを実行した。右側MBON01（bodyId 10013）へ接続するKCg-m 664細胞、合計15,147シナプスを使用した。これは脳全体のシミュレーションでも実際のハエの学習の検証でもない。

40訓練ブロック後の「Aを選ぶモデル確率」（30乱数シードの平均）：

| 条件 | Aを選ぶ確率 |
|---|---:|
| Aに報酬 | 98.70% |
| Bに報酬 | 1.30% |
| 報酬なし | 50.00% |
| 可塑性なし | 50.00% |
| A/Bに等しく報酬 | 50.02% |

数値は人為的な学習率・読み出し係数に依存する。ハエの正答率を示さない。等報酬条件の小さな偏りは、共通の活動細胞への二重更新と、その接続重みの刺激間差から生じる。

## 実データと仮定

- 実データ：公式v1.0、minconf 0.5の細胞注釈、KC→MBONの接続相手・シナプス数。全KC→MBONを抽出した61,210行も同梱。
- 対象は事前にKCg-m→右MBON01へ固定し、学習結果の良い細胞を探索して選んでいない。
- 初期重みはシナプス数を総和で割る。シナプス数が生理的強度と等しいという実証はない。
- 刺激A/Bは各々約10%のKCを直接活動させる乱数パターン。実在の匂い、嗅覚受容体、PNの応答ではない。重なりを許す。
- 報酬は外部から与えるスカラー。DAN細胞、報酬受容、スパイク、身体、回路内フィードバックは模擬していない。
- 活動したKCの接続を報酬に応じて減衰させる。MBON01全体の区画別ドーパミン作用を再現していない。
- 刺激ごとの学習前応答を参照して出力低下を価値へ変換する、人工的な読み出しを置く。実際のハエがこの正規化を行うという主張ではない。

## 計算

`w_i(0) = synapse_count_i / sum(synapse_count)`

`w_i(t+1) = w_i(t) * (1 - 0.08 * reward * x_i)`

`value(s) = 1 - sum_i[x_si*w_i(t)] / sum_i[x_si*w_i(0)]`

`P(A) = sigmoid(5 * (value(A)-value(B)))`

1ブロックはAとBを1回ずつ提示。40ブロック、30シード。評価は重みを変更しない読み出しのみ。等報酬対照では両刺激に0.5ずつ報酬を与え、1ブロックの報酬総量を揃えた。報酬B条件は最初からBで訓練した独立実験であり、学習途中の逆転学習ではない。

実接続を使っていても、この単純な課題は別の正の重みでも学べる。対照は学習ルールと報酬依存性の動作確認であり、male-cns固有の回路が必要だと示すものではない。実行した検証：無報酬・可塑性なしで50%維持、報酬対象変更で選好の向きが変化、重みが非負かつ初期値以下、接続ペア重複なし。実測行動との照合は未実施。

## 再実行

Python 3.12で検証。必要パッケージはnumpy、pandas、matplotlib（元データからの抽出時のみpyarrow）。同梱の抽出済みデータでオフライン再実行できる。

```bash
python -m pip install -r requirements.txt
python run_learning.py
```

この作業環境ではプロジェクトルートから `work/venv/bin/python outputs/run_learning.py`。

- `learning.png`：学習曲線（帯はシード間±1標準偏差）
- `learning_results.csv`：全条件・全シードの数値
- `learning_unit_edges.csv`：モデルに使った実接続
- `kc_mbon_edges.csv.gz` / `neurons.csv`：抽出した全KC→MBON接続と注釈
- `provenance.json`：元ファイルのSHA-256とサイズ
- `summary.json`：結果と設定

元ファイルを再取得する場合、公式ダウンロードページの `body-annotations-male-cns-v1.0-minconf-0.5.feather` と `connectome-weights-male-cns-v1.0-minconf-0.5.feather` を作業ディレクトリに `annotations.feather`, `weights.feather` として保存し、抽出済み出力のないディレクトリで `--raw 作業ディレクトリ` を指定する。元接続表は約1.1GB。

## 出典

- [MaleCNS公式データ](https://male-cns.janelia.org/download/)：FlyEM/Janelia、Cambridge/MRC LMB、Google Research。CC-BY。配布物はKC→MBONに抽出・整形したもの。
- [Hige et al., 2015, Coordinated and Compartmentalized Neuromodulation Shapes Sensory Processing in Drosophila](https://doi.org/10.1016/j.cell.2015.11.019)：区画ごとの可塑性の実験的背景。実装がこの論文を定量再現するわけではない。
- [Learning with reinforcement prediction errors in a model of the Drosophila mushroom body](https://www.nature.com/articles/s41467-021-22592-4)：KC→MBON可塑性を用いるモデルの背景。本実装はこの論文のモデルを再実装したものではない。
