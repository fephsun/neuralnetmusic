import theano
import theano.tensor as T
from theano.tensor.shared_randomstreams import RandomStreams
import numpy as np

from keras.layers.core import Layer

MIN_SD = 0.1

class NormalSampler(Layer):
	def __init__(self, axis_to_split, **kwargs):
		self.axis = axis_to_split
		self.rng = RandomStreams()
		super(NormalSampler, self).__init__(**kwargs)

	def get_output(self, train=False):
		inp = self.get_input(train)
		if self.axis == 2:
			new_axis_size = inp.shape[2] / 2
			new_size = (inp.shape[0], inp.shape[1], new_axis_size)
			mu, sigma = T.split(inp, [new_axis_size, new_axis_size], 2, axis=2)
			return mu + self.rng.normal(size=new_size) * sigma
		else:
			raise Exception('Other axes not implemented.')

	# def get_output(self, train=False):
	# 	return self.get_input(train)

class NormalProbCalculator(Layer):
	'''
	We break the layer interface here, because we need two inputs into this
	layer.  Therefore, NormalProbCalculator must be called from within another
	custom layer; Sequential cannot handle it.
	'''
	def __init__(self, axis_to_split, **kwargs):
		self.axis_to_split = axis_to_split
		self.param_input = None
		self.point = None
		super(NormalProbCalculator, self).__init__(**kwargs)

	def set_inputs(self, params, point):
		self.param_input = params
		self.point = point

	def get_output(self, train=False):
		params = self.param_input.get_output(train)
		if self.axis_to_split != 2:
			raise Exception('Other axes not implemented.')
		new_axis_size = params.shape[2] / 2
		mu, sigma = T.split(params, [new_axis_size, new_axis_size], 2, axis=2)
		err = T.mean(
			# Put a floor on the SD, to prevent division by 0.
			(mu - self.point)**2 / (sigma**2 + MIN_SD**2),
			axis=self.axis_to_split)
		return err
		# return (mu - self.point) / sigma

	# def get_output(self, train=False):
	# 	return self.param_input.get_output(train)

