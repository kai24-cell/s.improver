import os
import numpy as np
import librosa
import tensorflow as tf
from tensorflow.keras import layers, models
from sklearn.model_selection import train_test_split

def extract_features(file_path, sr=22050, max_frames=128):
    y, _ = librosa.load(file_path, sr=sr)
    mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
    mel_db = librosa.power_to_db(mel, ref=np.max)
    if mel_db.shape[1] < max_frames:
        mel_db = np.pad(mel_db, ((0,0),(0,max_frames - mel_db.shape[1])), mode='constant')
    else:
        mel_db = mel_db[:, :max_frames]
    return mel_db[..., np.newaxis]

# データとラベル準備
data_dir = "../data/train"  
X, y = [], []
for label, folder in enumerate(["speech", "music"]):
    folder_path = os.path.join(data_dir, folder)
    for fname in os.listdir(folder_path):
        if fname.endswith(".wav"):
            features = extract_features(os.path.join(folder_path, fname))
            X.append(features); y.append(label)

X = np.array(X); y = np.array(y)

# 訓練・検証分割
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

normalizer = layers.Normalization(input_shape=X_train.shape[1:])
normalizer.adapt(X_train)
# CNNモデル
model = models.Sequential([
    normalizer,
    layers.Conv2D(32,(3,3),activation='relu'),
    layers.Conv2D(32,(3,3),padding='same'),
    layers.BatchNormalization(),
    layers.Activation('relu'),
    layers.MaxPooling2D((2,2)),

    layers.Conv2D(64,(3,3),padding='same'),
    layers.BatchNormalization(),
    layers.Activation('relu'),
    layers.MaxPooling2D((2,2)),
    layers.Dropout(0.25),

    layers.Flatten(),
    layers.Dense(64),
    layers.BatchNormalization(),
    layers.Activation('relu'),
    layers.Dropout(0.5),
    layers.Dense(1,activation='sigmoid')
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model.fit(X_train, y_train, epochs=10, batch_size=16, validation_data=(X_val, y_val))
model.save('music_speech_cnn.keras')
