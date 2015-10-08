from keras.models import Sequential
import keras.optimizers as optimizers
from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM

from midi.utils import midiwrite

import numpy as np
import cPickle

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
	notes_input = np.concatenate((np.zeros((data.shape[0], 1, 88)), 
		data[:, :-1, :]), axis=1)
	notes_output = data

	print 'building model'
	model = Sequential()
	N_HIDDEN = 1024
	model.add(LSTM(88, N_HIDDEN, return_sequences=True))
	model.add(LSTM(N_HIDDEN, N_HIDDEN, return_sequences=True))
	model.add(LSTM(N_HIDDEN, 88, return_sequences=True))

	# optimizer = optimizers.SGD(lr=0.1)
	optimizer = optimizers.RMSprop()
	model.compile(loss='mse',
		optimizer=optimizer,
		class_mode='binary',)

	for iteration in range(500):
		print iteration
		model.fit(notes_input, notes_output, batch_size=128, nb_epoch=10)
		ideal_predict(model, data)
		if iteration % 10 == 0:
			print "saving weights"
			model.save_weights('D:/scratch/keras_model.hdf5', overwrite=True)
			print "done saving weights"

if __name__ == '__main__':
	main()
