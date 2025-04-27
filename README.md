# Audio Upsampler

FIRフィルタを用いたオーディオのアップサンプリング。

## インストール


**ソースディレクトリから:**

```bash
# フォルダをクローン
git clone <repo-url>  
cd audio_upsampler
pip install .
```

**ZIPから:**

```bash
pip install /path/to/audio_upsample.zip
```

## 使い方

```bash
upsample [OPTIONS] 入力ファイル 出力ファイル ターゲットサンプリングレート
```

```bash
python3 example.py
```

### 引数

- `入力ファイル`：元のオーディオファイルのパス
- `出力ファイル`：アップサンプリング後のファイル保存先
- `ターゲットサンプリングレート`：出力サンプリングレート (Hz)。入力サンプリングレートの整数倍である必要がある。

### オプション

- `--numtaps N`：フィルタタップ数 (デフォルト: 4096)
- `--beta B`：Kaiser窓のβパラメータ (デフォルト: 9.0)

## 例

```bash
upsample input.wav output.wav 96000 --numtaps 4096 --beta 9.0
```

