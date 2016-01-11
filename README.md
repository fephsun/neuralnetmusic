# neuralnetmusic
Felix's project for composing music using neural nets.

This is not in a state fit for public release right now, so play with at your own risk.  The myparser.py module turns musicxml files into training data.  The DBN.py module trains a DBN (deep belief network), and generates new music.  You need Theano to run.  There is a pre-trained model that you can play with.


## Requirements

You will need the following Python packages:

* Theano (see [installation instructions](http://deeplearning.net/software/theano/install.html))
* numpy (see [installation instructions](http://docs.scipy.org/doc/numpy-1.10.1/user/install.html))
* keras (see [installation instructions](https://github.com/fchollet/keras#installation))


## Usage

Using this project:

```bash
$ python DBN.py sample
```
