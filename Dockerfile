FROM python:3.9-slim

WORKDIR /app

# 音声処理に必要なシステムライブラリ (ffmpeg, libsndfile1)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*\
    flask-cors

# ライブラリのインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# フォルダの中身をすべてコピー
# (今回は必要なファイルしか置いていない前提なので .dockerignore すら不要です)
COPY . .

# Flaskサーバー起動
CMD ["python", "api.py"]