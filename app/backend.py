from pydub import AudioSegment
from pydub.effects import normalize
import numpy as np
import io
import os
import tensorflow as tf
import librosa

model=tf.keras.models.load_model('music_speech.cnn.keras')
TWO_FIFTEEN = 32768 - 1
fifty_per=0.5
#音声の特定の周波数帯域の音量を調整
"""
bands:強調する場所
gain:強調する音の大きさ
"""
def process_audio_mp3(file_path: str, tag: str, gains: list[float], output_path: str = None) -> str:#イコライザ変換する幅の指定
    audio = AudioSegment.from_mp3(file_path)
    rate, samples = mp3_to_np_array(audio)

    if tag == "song":
        bands = [(32, 64), (64, 125), (125, 250), (250, 500),#32,64なら32HZから64HZを指してる
                 (500, 1000), (1000, 2400), (2400, 4000),
                 (4000, 8000), (8000, 12500), (12500, 16500)]
        gains =[1.2,1.15,1.1,1.0,1.0,1.0,1.1,1.15,1.2,1.2]#1.0が100%で.0.1違うと10%変わる
    elif tag == "talk":
        bands = [(64, 120), (120, 250), (250, 500),
                 (500, 1000), (1000, 2400), (2400, 8000)]
        gains = [0.9,1.0,1.1,1.2,1.1,1.0]
    else:
        raise ValueError("分類失敗しました")

    processed = apply_equalizer(rate, samples, bands, gains)

    out_path = output_path or file_path.replace(".mp3", f"_{tag}_processed.mp3")
    return np_array_to_mp3(processed, rate, out_path)

def normalize_audio_mp3(file_path: str, output_path: str = None) -> str:#ノーマライズ曲の途中で音量が大きくなったり小さくなったりするするのを均一化する
    audio = AudioSegment.from_mp3(file_path)
    normalized_audio = normalize(audio)
    out_path = output_path or file_path.replace(".mp3", "_normalized.mp3")
    normalized_audio.export(out_path, format="mp3")
    return out_path

def mp3_to_np_array(audio: AudioSegment):#データをnumpy行列に変換、左右ごとに聞こえる音が分けられてる場合は平均化して1つに統一する
    samples = np.array(audio.get_array_of_samples())
    if audio.channels == 2:
        samples = samples.reshape((-1, 2)).mean(axis=1).astype(np.int16)
    return audio.frame_rate, samples

def np_array_to_mp3(samples: np.ndarray, rate: int, output_path: str):#配列データをmp3ファイルとして保存できる形にする
    audio = AudioSegment(
        samples.tobytes(),
        frame_rate=rate,
        sample_width=2,
        channels=1
    )
    audio.export(output_path, format="mp3")
    return output_path

def apply_equalizer(rate, data, bands, gains):#process_audio_mp3で指定した幅をイコライザ変換する処理
    freqs = np.fft.rfftfreq(len(data), d=1 / rate)
    fft_data = np.fft.rfft(data)
    gain_array = np.ones_like(freqs)

    for (low, high), gain in zip(bands, gains):
        gain_array[(freqs >= low) & (freqs <= high)] *= gain

    fft_data_eq = fft_data * gain_array
    processed_data = np.fft.irfft(fft_data_eq)
    processed_data = np.int16(processed_data / np.max(np.abs(processed_data)) * TWO_FIFTEEN)
    return processed_data

    
def reduce_noise(audio: AudioSegment, threshold_db: float = -35.0) -> AudioSegment:#ノイズ除去、一定以下の音声を削除
    samples = np.array(audio.get_array_of_samples())
    if audio.channels == 2:
        samples = samples.reshape((-1, 2)).mean(axis=1).astype(np.int16)

    max_amplitude = np.max(np.abs(samples))
    threshold = max_amplitude * (10 ** (threshold_db / 20))

    reduced_samples = np.where(np.abs(samples) < threshold, 0, samples).astype(np.int16)

    clean_audio = AudioSegment(
        reduced_samples.tobytes(),
        frame_rate=audio.frame_rate,
        sample_width=2,
        channels=1
    )
    return clean_audio

def backend_call(input_path, tag=None, gains=None):
    # 音声を読み込み → メルスペクトログラム作成
    y, sr = librosa.load(input_path, sr=22050)
    mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
    mel_db = librosa.power_to_db(mel, ref=np.max)
    max_frames = 128
    if mel_db.shape[1] < max_frames:
        mel_db = np.pad(mel_db, ((0,0),(0,max_frames - mel_db.shape[1])), mode='constant')
    else:
        mel_db = mel_db[:, :max_frames]
    X = mel_db[np.newaxis, ..., np.newaxis]  # (1, mel_bins, time_frames, 1)

    # 推論
    prediction = model.predict(X)
    pred_label = 'music' if prediction[0][0] > fifty_per else 'speech'#予測したmusic率50%以上でmusic
    print(f"{prediction[0][0]:.3f}は -> {pred_label}と判断されました")

    #音質向上処理開始
    audio = AudioSegment.from_mp3(input_path)
    #ノイズ除去
    processed_audio = reduce_noise(audio)
    #ノーマライズ
    processed_audio = normalize(processed_audio)
    #イコライザ変換
    rate, samples = mp3_to_np_array(audio=processed_audio)


    processed_audio = process_audio_mp3()
    # APIでJSONで返す形にする
    output_path = np_array_to_mp3(samples=processed_audio,rate=rate,output_path=input_path.replace(".mp3","_processed.mp3"))
    return output_path
