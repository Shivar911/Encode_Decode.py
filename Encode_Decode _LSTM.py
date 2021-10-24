from random import randint
from numpy import array
from numpy import argmax
from pandas import concat
from pandas import DataFrame
import pandas as pd
from keras.models import Sequential
from keras.layers import LSTM
from keras.layers import Dense
import csv

# generate a sequence of random numbers in [0, 99]
def generate_sequence(length=25):
  filename='numX.csv'
  balls=('b1','b2','b3','b4','b5','b6','b7','b8')
  data=pd.read_csv(filename, names=balls)
  ball1=array([data.b1])
  ball1=ball1.reshape(1,104,1)
  return [randint(0, 99) for _ in range(length)]

# one hot encode sequence
def one_hot_encode(sequence, n_unique=100):
	encoding = list()
	for value in sequence:
		vector = [0 for _ in range(n_unique)]
		vector[value] = 1
		encoding.append(vector)
	return array(encoding)

# decode a one hot encoded string
def one_hot_decode(encoded_seq):
	return [argmax(vector) for vector in encoded_seq]

# generate data for the lstm
def generate_data():
	# generate sequence
	sequence = generate_sequence()
	# one hot encode
	encoded = one_hot_encode(sequence)
	# create lag inputs
	df = DataFrame(encoded)
	df = concat([df.shift(4), df.shift(3), df.shift(2), df.shift(1), df], axis=1)
	# remove non-viable rows
	values = df.values
	values = values[5:,:]
	# convert to 3d for input
	X = values.reshape(len(values), 5, 100)
	# drop last value from y
	y = encoded[4:-1,:]
	return X, y

# define model
model = Sequential()
model.add(LSTM(50, batch_input_shape=(5, 5, 100), stateful=True))
model.add(Dense(100, activation='softmax'))
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
# fit model
for i in range(2000):
	X, y = generate_data()
	model.fit(X, y, epochs=1, batch_size=5, verbose=2, shuffle=False)
	model.reset_states()
# evaluate model on new data
X, y = generate_data()
yhat = model.predict(X, batch_size=5)
print('Expected:  %s' % one_hot_decode(y))
print('Predicted: %s' % one_hot_decode(yhat))