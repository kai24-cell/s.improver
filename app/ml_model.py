import sys
import os
import librosa
import numpy as np

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, "../music-auto_tagging-keras"))
sys.path.append(parent_dir)

import audio_processor as ap
import tensorflow as tf

audio_path = os.path.join(parent_dir, "data", "sample_talk_02.mp3")#調べるファイル
y, sr = librosa.load(audio_path, sr=None)#音声の読み込み
print(audio_path)
melgram = ap.compute_melgram(audio_path) #メルスペクトログラムを作成

print(melgram.shape)  # 数字に分けてジャンルを分類する前段階を整えてる
# melgram の一部を確認

harmonic, percussive = librosa.effects.hpss(y)
vocal_ratio = np.sum(harmonic**2) / (np.sum(y**2) + 1e-10)
print("vocal_ratio:", vocal_ratio)

if vocal_ratio > 0.55:
    tag = "歌"
    print("歌")
else:
    tag = "トーク"
    print("トーク")
    
print("分類タグ:", tag)