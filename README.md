# Male CNS — Learning & Neural Space

雄ショウジョウバエのmale-cns:v1.0の実接続と実測神経骨格を使った、最小学習モデルとインタラクティブな3D可視化。

## 可視化

```sh
python3 -m http.server 8000
```

ブラウザで http://localhost:8000/outputs/neural-space.html を開くと、33ニューロンの3D形状を回転・拡大できる。PLAYで全664細胞の学習結果に同期して表示が変化する。Three.jsはCDNから読み込むためネットワーク接続が必要。

- [3D Neural Space](outputs/neural-space.html)
- [細胞別の学習可視化](outputs/learning-interactive.html)
- [学習モデルの仕様・結果・制約](outputs/README.md)

## 再実行

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r outputs/requirements.txt
python outputs/run_learning.py
```

抽出済み接続データを同梱しているため、約1.1GBの元接続表を再取得せず学習実験を再実行できる。可視化は実行時点の結果を埋め込んだスナップショットで、再実行結果へ自動更新されない。

## 実データと演出

- 学習：KCg-m 664細胞 → 右MBON01（body ID 10013）、15,147シナプス。
- 3D：664細胞から32個のKCを抽出し、MBON01と合わせて33個の公式SWC骨格を表示。Aで活動する細胞からシナプス数上位12個、未選択のB活動細胞から上位12個、非活動細胞から上位8個を選択。
- 形状は実測骨格の枝分かれと末端を保持して間引いたもの。元座標は8nm voxel単位。3D表示時に全体を中心化・等方スケーリング。
- 刺激、可塑性、価値の読み出しは仮定。発光点の移動は演出であり、発火・伝導のシミュレーションではない。
- 実際のハエの学習や行動を再現・検証したという主張ではない。この課題がmale-cns固有の配線を必要とすることも示していない。

## 出典

[MaleCNS公式データ](https://male-cns.janelia.org/download/) — FlyEM/Janelia、Cambridge/MRC LMB、Google Research。データはCC-BY。接続表の抽出・整形、骨格の間引き・可視化を行っている。元接続表のハッシュは `outputs/provenance.json` に記録。

骨格取得元：`https://storage.googleapis.com/flyem-male-cns/v1.0/segmentation/skeletons-malecns/skeletons-swc/{bodyId}.swc`

`visualizations/` は編集用のインライン断片、`outputs/` は再実行コード・データ・結果・ブラウザ用の完成版。作業用環境と大容量の元データはGit管理対象外。
