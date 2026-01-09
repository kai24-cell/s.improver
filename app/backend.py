import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))#pydubがffmpegを見つけられるようにパスを通す
os.environ["PATH"] += os.pathsep + BASE_DIR

from pydub import AudioSegment
from pydub.effects import normalize
import numpy as np
import tensorflow as tf
import librosa
import azure.cognitiveservices.speech as speechsdk
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
load_dotenv()

SPEECH_KEY = os.getenv("SPEECH_KEY")
SPEECH_REGION = os.getenv("SPEECH_REGION")
LANGUAGE_KEY = os.getenv("LANGUAGE_KEY")
LANGUAGE_ENDPOINT = os.getenv("LANGUAGE_ENDPOINT")
try:
    model_path = os.path.join(BASE_DIR, 'music_speech_cnn.keras')
    model=tf.keras.models.load_model(model_path)
except:
    print("モデルの読み取りに失敗しました")
    model=None
    
TWO_FIFTEEN = 32768 - 1
fifty_per=0.5

def analyze_speech_content(audio_path):
    temp_wav ="temp_for_azure.wav"
    try:
        sound = AudioSegment.from_file(audio_path)
        sound.export(temp_wav, format="wav")
    except Exception as e:
        print(f"変換エラー: {e}")
        return None

    #音声認識 (Speech to Text)
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    speech_config.speech_recognition_language = "ja-JP" 
    
    audio_config = speechsdk.audio.AudioConfig(filename=temp_wav)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    print("文字起こし実行中...")
    result = speech_recognizer.recognize_once_async().get()
    
    transcribed_text = ""
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        transcribed_text = result.text
        print(f"文字起こし結果: {transcribed_text}")
    else:
        print("音声認識できませんでした (無音またはノイズ)")
        if os.path.exists(temp_wav):
            os.remove(temp_wav)
        return None

    # キーフレーズ抽出 (Language Service)
    tags = []
    if transcribed_text:
        try:
            ta_client = TextAnalyticsClient(endpoint=LANGUAGE_ENDPOINT, credential=AzureKeyCredential(LANGUAGE_KEY))
            documents = [transcribed_text]
            response = ta_client.extract_key_phrases(documents=documents)[0]
            if not response.is_error:
                tags = response.key_phrases
                print(f"抽出タグ: {tags}")
            else:
                print(f"タグ抽出エラー: {response.error}")
        except Exception as e:
            print(f"Language API エラー: {e}")

    # 一時ファイルの削除
    if os.path.exists(temp_wav):
        try:
            import gc
            if 'speech_recognizer' in locals():
                del speech_recognizer
            gc.collect()
            
            os.remove(temp_wav)
        except Exception:
            print("一時ファイルがロックされており削除できませんでした（無視します）")
            pass
        
    return {"text": transcribed_text, "tags": tags}




#音声の特定の周波数帯域の音量を調整
"""
bands:強調する場所
gain:強調する音の大きさ
"""
def process_audio_mp3(audio_segment: AudioSegment, tag: str, output_path: str = None) -> str:#イコライザ変換する幅の指定
    rate, samples = mp3_to_np_array(audio_segment)

    if tag == "music":
        bands = [(32, 64), (64, 125), (125, 250), (250, 500),#32,64なら32HZから64HZを指してる
                 (500, 1000), (1000, 2400), (2400, 4000),
                 (4000, 8000), (8000, 12500), (12500, 16500)]
        gains =[1.2,1.15,1.1,1.0,1.0,1.0,1.1,1.15,1.2,1.2]#1.0が100%で.0.1違うと10%変わる
    elif tag == "speech":
        bands = [(64, 120), (120, 250), (250, 500),
                 (500, 1000), (1000, 2400), (2400, 8000)]
        gains = [0.9,1.0,1.1,1.2,1.1,1.0]
    else:
        raise ValueError("タグ付け分類失敗しました")

    processed = apply_equalizer(rate, samples, bands, gains)
    
    
    return np_array_to_mp3(processed, rate,output_path)

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
    max_val = np.max(np.abs(processed_data))
    
    #無音だったときprocessed_data÷0にならないようにケアしてる
    if max_val > 0:
        processed_data = (processed_data / max_val ) * TWO_FIFTEEN

    processed_data=np.int16(processed_data)
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

def backend_call(input_path):
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
    audio = AudioSegment.from_file(input_path)
    #ノイズ除去
    processed_audio = reduce_noise(audio)
    #ノーマライズ
    processed_audio = normalize(processed_audio)
    #イコライザ変換

    output_path = input_path.replace(".mp3", "_processed.mp3")
    processed_audio = process_audio_mp3(audio_segment=processed_audio,tag=pred_label,output_path=output_path)

    #テキスト機能
    ai_data = None
    if pred_label == "speech":
        ai_data = analyze_speech_content(processed_audio)
        if ai_data:
            txt_path = processed_audio.replace(".mp3", ".txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(f"Transcript: {ai_data['text']}\n")
                f.write(f"Tags: {', '.join(ai_data['tags'])}")
    return processed_audio,ai_data