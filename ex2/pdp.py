#!/usr/bin/env python3

import sys
import os

import pandas as pd
import numpy as np

from sklearn.preprocessing import minmax_scale
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt

DIR_NAME = "pdp"

def pdp(data, eval_function, features, means, stds, resolution=100, n_data=100):

	index = np.random.permutation(data.shape[0])[:n_data]
	downsampled_data = data[index,:]

	pdps = np.zeros((data.shape[1], resolution))
	print(list(zip(features, list(means))))

	for i, feature in enumerate(features):
		minimum, maximum = data[:,i].min(), data[:,i].max()
		minimum_rescaled, maximum_rescaled = minimum*stds[i]+means[i], maximum*stds[i]+means[i]
		print ('Processing feature %d: %s. Min: %.3f, Max: %.3f' % (i, feature, minimum_rescaled, maximum_rescaled))
		for j_index, j in enumerate(np.linspace(minimum, maximum, num=resolution)):
			dd_cpy = downsampled_data.copy()
			dd_cpy[:,i] = j
			pdps[i,j_index] = np.mean(eval_function(dd_cpy)[:,0])

		rescaled = np.linspace(minimum_rescaled, maximum_rescaled, num=resolution)
		plt.plot(rescaled, pdps[i,:])
		plt.xlabel('Feature')
		plt.ylabel('Mean probability')
		plt.title(feature)
		os.makedirs(DIR_NAME, exist_ok=True)
		plt.savefig(DIR_NAME+'/%s.pdf' % feature)
		plt.close()

if __name__=="__main__":
	data = pd.read_csv(sys.argv[1]).fillna(0)

	labels = data['Label'].values

	#CAIA
	data = data.drop(columns=[
		'flowStartMilliseconds',
		'sourceIPAddress',
		'destinationIPAddress',
		'Label',
		'Attack' ])

	#AGM
	#data = data.drop (columns=[
		#'flowStartMilliseconds',
		#'sourceIPAddress',
		#'mode(destinationIPAddress)',
		#'mode(_tcpFlags)',
		#'Label',
		#'Attack' ])

	features = data.columns

	# TODO: downsampling ?
	# TODO: one-hot encoding ?

	data = minmax_scale(data)

	rf = RandomForestClassifier(n_estimators=10)
	rf.fit (data, labels)

	pdp(data, rf.predict_proba, features, means=[0]*data.shape[1], stds=[1]*data.shape[1])