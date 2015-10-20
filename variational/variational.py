import theano
import theano.tensor as T
import numpy as np

from keras.layers.core import Layer

class VariationalWrapper(Layer):
	'''
	Creates a variational "autoencoder", given an encoding model P(z|x), a
	decoding model P(x|z), and the associated probabilistic models.  The output
	of this net is a numerical value P(x|z), so this layer is not terribly
	composible.

	decoder_prob and encoder_prob take in two inputs: a set of distribution 
	parameters and a data point.  These functions determine the probability of
	the data point, given the distribution parameters.  This is a rather hacky
	way to allow Theano to calculate a distribution probability.
	'''
	def __init__(self, n_iters, seq_length, z_size,
			encoder_net, encoder_prob, encoder_sampler,
			decoder_net, decoder_prob, **kwargs):
		self.n_iters = n_iters
		self.seq_length = seq_length
		self.z_size = z_size

		self.encoder_net = encoder_net
		self.encoder_prob = encoder_prob
		self.encoder_sampler = encoder_sampler
		self.encoder_sampler.set_previous(self.encoder_net)

		self.decoder_net = decoder_net
		self.decoder_prob = decoder_prob

		self.params = self.encoder_net.params + self.decoder_net.params
		self.regularizers = self.encoder_net.regularizers \
			+ self.decoder_net.regularizers
		self.constraints = self.encoder_net.constraints \
			+ self.decoder_net.constraints
		self.updates = self.encoder_net.updates + self.decoder_net.updates

		super(VariationalWrapper, self).__init__(**kwargs)

	def sample_z(self, prior_result, train=0):
		return prior_result + self.encoder_sampler.get_output(bool(train))

	def get_output(self, train=False):
		# Use theano scan to estimate z|x.
		inp = self.get_input(train)
		estimate = T.zeros((inp.shape[0], self.seq_length, self.z_size), dtype=inp.dtype)
		for i in range(self.n_iters):
			estimate += self.encoder_sampler.get_output(train)
		z_estimate = estimate / self.n_iters
		# scan_results, _ = theano.scan(
		# 	self.sample_z,
		# 	outputs_info=T.zeros_like(inp),
		# 	non_sequences=int(train),	# Theano tensor variable bs.
		# 	n_steps=self.n_iters,
		# )
		# z_estimate = scan_results[-1] / self.n_iters
		self.decoder_net.layers[0].input = z_estimate

		# Return the total error.
		self.encoder_prob.set_inputs(self.encoder_net, z_estimate)
		self.decoder_prob.set_inputs(self.decoder_net, inp)
		return self.decoder_prob.get_output(train) + self.encoder_prob.get_output(train)

	def get_input(self, train=False):
		return self.encoder_net.get_input(train)

