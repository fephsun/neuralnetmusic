from keras.models import Sequential
import keras.optimizers as optimizers
from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.layers.containers import Sequential as SequentialLayer

from midi.utils import midiwrite

import numpy as np
import cPickle

from variational.variational import VariationalWrapper
from variational.distributions import NormalSampler, NormalProbCalculator

def sample(model, length=64):
	x = np.zeros((65, 88))
	x = np.expand_dims(x, axis=0)
	for step in range(length):
		pred = model.predict(x[:, :step+1, :])
		print pred[0]
		x[0, step+1, :] = np.round(pred[0])
	return x[0, 1:, :]

def ideal_predict(model, data):
	inp = data[0, :, :]
	inp = np.expand_dims(inp, axis=0)
	out = model.predict(inp)
	print out.shape
	print np.max(out)
	midiwrite('./test.midi', np.round(out[0, :, :]), r=(12, 109), dt=64)

def sample_and_save(model, length=64):
	x = sample(model, length)
	midiwrite('./test.midi', x, r=(12, 109), dt=64)

def load_data():
	all_data = cPickle.load(open('./joplin_data.pickle', 'rb'))
	n_samples = all_data.shape[0]
	three_d_data = np.zeros((n_samples, 64, 88))
	for i in range(n_samples):
		three_d_data[i, :, :] = all_data[i, :].reshape((88, 64)).T
	return three_d_data

def main():
	data = load_data()

	print 'building model'
	SEQ_LENGTH = data.shape[1]
	N_INPUT = 88
	N_HIDDEN = 160
	Z_SIZE = 8
	net_z_given_x = SequentialLayer()
	net_z_given_x.add(LSTM(N_HIDDEN, return_sequences=True,
		input_length=SEQ_LENGTH, input_dim=N_INPUT))
	net_z_given_x.add(LSTM(Z_SIZE*2, return_sequences=True))
	net_x_given_z = SequentialLayer()
	net_x_given_z.add(LSTM(N_HIDDEN, return_sequences=True,
		input_length=SEQ_LENGTH, input_dim=Z_SIZE))
	net_x_given_z.add(LSTM(N_INPUT*2, return_sequences=True))
	sampler_z_given_x = NormalSampler(axis_to_split=2)
	prob_z_given_x = NormalProbCalculator(axis_to_split=2)
	prob_x_given_z = NormalProbCalculator(axis_to_split=2)
	variational = VariationalWrapper(1, SEQ_LENGTH, Z_SIZE,
		net_z_given_x, prob_z_given_x, sampler_z_given_x,
		net_x_given_z, prob_x_given_z)
	model = Sequential()
	model.add(variational)

	# optimizer = optimizers.SGD(lr=0.01)
	optimizer = optimizers.RMSprop()
	model.compile(loss='mae',
		optimizer=optimizer,)

	for iteration in range(500):
		print iteration
		model.fit(data, np.zeros((data.shape[0], SEQ_LENGTH)),
			batch_size=128, nb_epoch=10)
		if iteration % 10 == 0:
			print "saving weights"
			model.save_weights('D:/scratch/keras_model_simple.hdf5', overwrite=True)
			print "done saving weights"

if __name__ == '__main__':
	main()
