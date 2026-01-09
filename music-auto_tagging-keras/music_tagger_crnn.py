# -*- coding: utf-8 -*-
'''MusicTaggerCRNN model for Keras (Updated for TF 2.x).'''
from tensorflow.keras import backend as K
from tensorflow.keras.layers import Input, Dense, Dropout, Reshape, Permute
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Conv2D, MaxPooling2D, ZeroPadding2D, BatchNormalization, ELU, GRU
from tensorflow.keras.utils import get_file

TH_WEIGHTS_PATH = 'https://github.com/keunwoochoi/music-auto_tagging-keras/blob/master/data/music_tagger_crnn_weights_theano.h5'
TF_WEIGHTS_PATH = 'https://github.com/keunwoochoi/music-auto_tagging-keras/blob/master/data/music_tagger_crnn_weights_tensorflow.h5'


def MusicTaggerCRNN(weights='msd', input_tensor=None,
                    include_top=True):
    '''Instantiate the MusicTaggerCRNN architecture.'''

    if weights not in {'msd', None}:
        raise ValueError('The `weights` argument should be either '
                         '`None` (random initialization) or `msd` '
                         '(pre-training on Million Song Dataset).')

 
    data_format = K.image_data_format()
    
    if data_format == 'channels_first':
        input_shape = (1, 96, 1366)
        channel_axis = 1
        freq_axis = 2
        time_axis = 3
    else:
        input_shape = (96, 1366, 1)
        channel_axis = 3
        freq_axis = 1
        time_axis = 2

    if input_tensor is None:
        melgram_input = Input(shape=input_shape)
    else:
        if not K.is_keras_tensor(input_tensor):
            melgram_input = Input(tensor=input_tensor, shape=input_shape)
        else:
            melgram_input = input_tensor

   
    x = ZeroPadding2D(padding=(0, 37))(melgram_input)
    x = BatchNormalization(axis=freq_axis, name='bn_0_freq')(x)


    x = Conv2D(64, (3, 3), padding='same', name='conv1')(x)
    x = BatchNormalization(axis=channel_axis, name='bn1')(x)
    x = ELU()(x)
    x = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), name='pool1')(x)
    x = Dropout(0.1, name='dropout1')(x)

    
    x = Conv2D(128, (3, 3), padding='same', name='conv2')(x)
    x = BatchNormalization(axis=channel_axis, name='bn2')(x)
    x = ELU()(x)
    x = MaxPooling2D(pool_size=(3, 3), strides=(3, 3), name='pool2')(x)
    x = Dropout(0.1, name='dropout2')(x)


    x = Conv2D(128, (3, 3), padding='same', name='conv3')(x)
    x = BatchNormalization(axis=channel_axis, name='bn3')(x)
    x = ELU()(x)
    x = MaxPooling2D(pool_size=(4, 4), strides=(4, 4), name='pool3')(x)
    x = Dropout(0.1, name='dropout3')(x)


    x = Conv2D(128, (3, 3), padding='same', name='conv4')(x)
    x = BatchNormalization(axis=channel_axis, name='bn4')(x)
    x = ELU()(x)
    x = MaxPooling2D(pool_size=(4, 4), strides=(4, 4), name='pool4')(x)
    x = Dropout(0.1, name='dropout4')(x)

  
    if data_format == 'channels_first':
        x = Permute((3, 1, 2))(x)
    
    x = Reshape((15, 128))(x)

    x = GRU(32, return_sequences=True, name='gru1')(x)
    x = GRU(32, return_sequences=False, name='gru2')(x)
    x = Dropout(0.3)(x)
    
    if include_top:
        x = Dense(50, activation='sigmoid', name='output')(x)


    model = Model(melgram_input, x)
    
    if weights is None:
        return model
    else: 
        if data_format == 'channels_last':
             print("Warning: Pre-trained weights might require 'channels_first' format.")
        
        return model