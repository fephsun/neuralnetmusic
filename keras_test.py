from keras.models import Sequential
from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
import numpy as np
import cPickle

print 'loading data'
data = cPickle.load(open('keras_data.pickle', 'rb'))

print 'building model'
model = Sequential()
model.add(LSTM(88, 128, return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(128, 88, return_sequences=False))
model.add(Dropout(0.2))

model.compile(loss='mse',
	optimizer='rmsprop',
	class_mode='binary',)

for iteration in range(50):
	print 'iteration ', iteration
	for fname, notes in data.iteritems():
		notes_input = np.expand_dims(notes.T, axis=0)
		model.fit(notes_input, notes.T, batch_size=128, nb_epoch=1)

