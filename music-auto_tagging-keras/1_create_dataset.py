import os
import glob
import librosa
import soundfile as sf
import pandas as pd
import numpy as np
from tqdm import tqdm
import warnings

TARGET_SR = 22050  
SEGMENT_SEC = 3.0  # 3秒でわける
SEGMENT_SAMPLES = int(TARGET_SR * SEGMENT_SEC)

#小さいほど厳しくカット
VAD_TOP_DB = 25 

# 各カテゴリの目標ファイル数
TARGET_SPEECH_COUNT = 5000
TARGET_MUSIC_COUNT_PER_TYPE = 1667 # 3種類で合計 約5000
TARGET_VOCAL_COUNT = 1666 

SOURCE_LIBRISPEECH = os.path.join('1_Source_Data', 'LibriSpeech', 'train-clean-100')
SOURCE_VOCALSET = os.path.join('1_Source_Data', 'FULL')
SOURCE_FMA_AUDIO = os.path.join('1_Source_Data', 'fma_small')
SOURCE_FMA_META = os.path.join('1_Source_Data', 'fma_metadata', 'tracks.csv')

# 完成品（3秒）の出力先パス
DEST_SPEECH = os.path.join('data', 'train', 'speech')
DEST_MUSIC = os.path.join('data', 'train', 'music')

def create_segments(source_dir, file_extension, dest_dir, target_count, prefix):
   
    print(f"\nProcessing {prefix}...")
    # フォルダがなければ作成
    os.makedirs(dest_dir, exist_ok=True)

    file_paths = glob.glob(os.path.join(source_dir, '**', f'*.{file_extension}'), recursive=True)
    
    if not file_paths:
        print(f"  [ERROR] No files found in: {source_dir}")
        print("  Please check your folder structure (Step 0).")
        return

    segment_counter = 0
    pbar = tqdm(total=target_count, desc=f"Creating {prefix} segments")
    
    for file_path in file_paths:
        if segment_counter >= target_count:
            break
            
        try:
            # warningsを抑制して、mp3の警告（FMA）を無視
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                y, sr = librosa.load(file_path, sr=TARGET_SR, mono=True)
            
            y_trimmed, _ = librosa.effects.trim(y, top_db=VAD_TOP_DB)
            num_segments = len(y_trimmed) // SEGMENT_SAMPLES
            
            for i in range(num_segments):
                if segment_counter >= target_count:
                    break
                    
                segment = y_trimmed[i * SEGMENT_SAMPLES : (i + 1) * SEGMENT_SAMPLES]
                
                original_name = os.path.basename(file_path).split('.')[0]
                save_name = f"{prefix}_{original_name}_seg{i}.wav"
                save_path = os.path.join(dest_dir, save_name)
                
                sf.write(save_path, segment, TARGET_SR)
                
                segment_counter += 1
                pbar.update(1)

        except Exception as e:
            pass
            
    pbar.close()
    if segment_counter < target_count:
        print(f"  [Warning] Reached end of files. Created {segment_counter} / {target_count} segments.")
    else:
        print(f"  Successfully created {segment_counter} segments.")


def create_fma_segments(fma_audio_dir, fma_tracks_csv, dest_dir, target_count, prefix, genre_filter):
    print(f"\nProcessing {prefix} (from FMA)...")
    os.makedirs(dest_dir, exist_ok=True)
    
    try:
        tracks_df = pd.read_csv(fma_tracks_csv, header=[0, 1], index_col=0)
    except Exception as e:
        print(f"  [ERROR] Could not read {fma_tracks_csv}: {e}")
        print("  Please check your fma_metadata download (Step 0).")
        return
    small_subset_mask = tracks_df[('set', 'subset')] == 'small'
    
    if genre_filter == 'Instrumental':
        genre_mask = tracks_df[('track', 'genre_top')] == 'Instrumental'
        target_tracks = tracks_df[small_subset_mask & genre_mask]
    else:
        genre_mask = tracks_df[('track', 'genre_top')] != 'Instrumental'
        target_tracks = tracks_df[small_subset_mask & genre_mask]
        
    file_ids = target_tracks.index.values
    
    segment_counter = 0
    pbar = tqdm(total=target_count, desc=f"Creating {prefix} segments")
    
    np.random.shuffle(file_ids) 
    
    for file_id in file_ids:
        if segment_counter >= target_count:
            break
            
        try:
            file_id_str = f"{file_id:06d}" 
            folder_str = file_id_str[:3]   
            file_path = os.path.join(fma_audio_dir, folder_str, f"{file_id_str}.mp3")

            if not os.path.exists(file_path):
                continue
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                y, sr = librosa.load(file_path, sr=TARGET_SR, mono=True)
            
            y_trimmed, _ = librosa.effects.trim(y, top_db=VAD_TOP_DB)
            num_segments = len(y_trimmed) // SEGMENT_SAMPLES
            
            for i in range(num_segments):
                if segment_counter >= target_count:
                    break
                segment = y_trimmed[i * SEGMENT_SAMPLES : (i + 1) * SEGMENT_SAMPLES]
                save_name = f"{prefix}_{file_id_str}_seg{i}.wav"
                save_path = os.path.join(dest_dir, save_name)
                sf.write(save_path, segment, TARGET_SR)
                segment_counter += 1
                pbar.update(1)

        except Exception as e:
            pass
            
    pbar.close()
    if segment_counter < target_count:
        print(f"  [Warning] Reached end of files. Created {segment_counter} / {target_count} segments.")
    else:
        print(f"  Successfully created {segment_counter} segments.")

if __name__ == "__main__":
    print("--- Starting Dataset Creation ---")

    create_segments(
        source_dir=SOURCE_LIBRISPEECH,
        file_extension='flac',
        dest_dir=DEST_SPEECH,
        target_count=TARGET_SPEECH_COUNT,
        prefix='speech_libri'
    )

    create_segments(
        source_dir=SOURCE_VOCALSET,
        file_extension='wav',
        dest_dir=DEST_MUSIC,
        target_count=TARGET_MUSIC_COUNT_PER_TYPE,
        prefix='music_acapella'
    )

    create_fma_segments(
        fma_audio_dir=SOURCE_FMA_AUDIO,
        fma_tracks_csv=SOURCE_FMA_META,
        dest_dir=DEST_MUSIC,
        target_count=TARGET_MUSIC_COUNT_PER_TYPE,
        prefix='music_instrumental',
        genre_filter='Instrumental'
    )
    
    create_fma_segments(
        fma_audio_dir=SOURCE_FMA_AUDIO,
        fma_tracks_csv=SOURCE_FMA_META,
        dest_dir=DEST_MUSIC,
        target_count=TARGET_VOCAL_COUNT,
        prefix='music_vocal',
        genre_filter='Vocal'
    )

    print("\n--- All processing complete! ---")
    print(f"Check your folders: \n{DEST_SPEECH} \n{DEST_MUSIC}")