from keras.models import Sequential, load_model, Model
from keras.layers import Input, Dense, Conv2D, Flatten, BatchNormalization, Activation, LeakyReLU, add, ReLU, Concatenate
from keras.optimizers import SGD
from keras import regularizers

import keras.backend as K
import tensorflow as tf

import config

class Gen_Model():
    def __init__(self, reg_const, learning_rate, input_dim):
        self.reg_const = reg_const
        self.learning_rate = learning_rate
        self.input_dim = input_dim

    def predict(self, x):
        return self.model.predict(x)

    def fit(self, states, targets, epochs, verbose, validation_split, batch_size):
        return self.model.fit(states, targets, epochs=epochs, verbose=verbose, validation_split = validation_split, batch_size = batch_size)

    def write(self, version):
        self.model.save_weights(config.folder_agents + '\\' + "{0:0>5}".format(version) + '.h5')

    def read(self, version):
        return self.model.load_weights( config.folder_agents + '\\' + "{0:0>5}".format(version) + '.h5')

class Residual_CNN(Gen_Model):
    def __init__(self, reg_const, learning_rate, input_dim):
        Gen_Model.__init__(self, reg_const, learning_rate, input_dim)
        self.model = self._build_model()

    def value_head(self, x):
        x = Dense(
            150
            , use_bias=False
            , activation='linear'
            , kernel_regularizer=regularizers.l2(self.reg_const)
            , name = 'value_dense'
            )(x)

        x = BatchNormalization()(x)
        x = LeakyReLU(name='value_leaky_1')(x)

        x = Dense(
            100
            , use_bias=False
            , activation='linear'
            , kernel_regularizer=regularizers.l2(self.reg_const)
            , name = 'value_dense_2'
            )(x)

        x = BatchNormalization()(x)
        x = LeakyReLU(name='value_leaky_2')(x)

        x = Dense(
            75
            , use_bias=False
            , activation='linear'
            , kernel_regularizer=regularizers.l2(self.reg_const)
            , name = 'value_dense_3'
            )(x)

        x = BatchNormalization()(x)
        x = LeakyReLU(name='value_leaky_3')(x)

        x = Dense(
            50
            , use_bias=False
            , activation='linear'
            , kernel_regularizer=regularizers.l2(self.reg_const)
            , name = 'value_dense_4'
            )(x)

        x = BatchNormalization()(x)
        x = LeakyReLU(name='value_leaky_4')(x)

        x = Dense(
            15
            , use_bias=False
            , activation='linear'
            , kernel_regularizer=regularizers.l2(self.reg_const)
            , name = 'value_dense_5'
            )(x)

        x = BatchNormalization()(x)
        x = LeakyReLU(name='value_leaky_5')(x)

        x = Dense(
            1
            , use_bias=False
            , activation='tanh'
            , kernel_regularizer=regularizers.l2(self.reg_const)
            , name = 'value_head'
            )(x)

        return (x)

    def _build_model(self):
        main_input = Input(shape = self.input_dim, name = 'main_input')

        vh = self.value_head(main_input)
        #ph = self.policy_head(x)

        model = Model(inputs=[main_input], outputs=[vh])
        model.compile(loss={'value_head': 'mean_squared_error'},
            optimizer=SGD(lr=self.learning_rate, momentum = config.MOMENTUM),	
            #loss_weights={'value_head': 1.0}	
            )

        return model