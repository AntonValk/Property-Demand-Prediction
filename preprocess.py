import numpy as np
import pandas as pd
import seaborn as sns
import networkx as nx 
from scipy import sparse
import scipy.spatial.distance
import matplotlib.pyplot as plt
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer


def preprocess_data_1(fraction_test = 0.333):
	df = pd.read_json(open("train.json", "r"))

	df["num_photos"] = df["photos"].apply(len)
	df["num_features"] = df["features"].apply(len)
	df["num_description_words"] = df["description"].apply(lambda x: len(x.split(" ")))
	df["created"] = pd.to_datetime(df["created"])
	df["created_month"] = df["created"].dt.month
	df["created_day"] = df["created"].dt.day

	num_feats = ["bathrooms", "bedrooms", "latitude", "longitude", "price",
	             "num_photos", "num_features", "num_description_words",
	             "created_month", "created_day"]
	X = df[num_feats]
	y = df["interest_level"]

	X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=fraction_test)
	return X_train, X_val, y_train, y_val

# need to fix this there is a bug in this method
def preprocess_data_2(fraction_test = 0.333):
	df = pd.read_json(open("train.json", "r"))

	df["num_photos"] = df["photos"].apply(len)
	df["num_features"] = df["features"].apply(len)
	df["num_description_words"] = df["description"].apply(lambda x: len(x.split(" ")))
	df["created"] = pd.to_datetime(df["created"])
	df["created_month"] = df["created"].dt.month
	df["created_day"] = df["created"].dt.day

	num_feats = ["bathrooms", "bedrooms", "latitude", "longitude", "price",
	             "num_photos", "num_features", "num_description_words",
	             "created_month", "created_day"]

	# Encode categorical features
	categorical = ["display_address", "manager_id", "building_id", "street_address"]
	for f in categorical:
	        if df[f].dtype=='object':
	            #print(f)
	            lbl = preprocessing.LabelEncoder()
	            lbl.fit(list(df[f].values))
	            df[f] = lbl.transform(list(df[f].values))
	            num_feats.append(f)


	# We have features column which is a list of string values. 
	# So we can first combine all the strings together to get a single string and then apply count vectorizer on top of it.
	df['features'] = df["features"].apply(lambda x: " ".join(["_".join(i.split(" ")) for i in x]))
	tfidf = CountVectorizer(stop_words='english', max_features=50)
	tr_sparse = tfidf.fit_transform(df["features"])

	train_X = sparse.hstack([df[num_feats], tr_sparse]).tocsr()

	target_num_map = {'high':0, 'medium':1, 'low':2}
	train_y = np.array(df['interest_level'].apply(lambda x: target_num_map[x]))

	# print('Total data shape:', train_X.shape)
	split = int(train_X.shape[0] * fraction_test)
	# print(train_X[split])
	# print()
	# print(train_X[split-1])
	# print()
	# print(train_X[split+1])
	train_X = train_X[:-split]
	train_y = train_y[:-split]
	test_X = train_X[-split:]
	test_y = train_y[-split:]
	# print()
	# print(test_X[0])
	# print(train_X.shape, test_X.shape, train_y.shape, test_y.shape)
	# print(train_X.shape[0] + test_X.shape[0])
	return train_X, test_X, train_y, test_y


def preprocessing_graph_1(fraction_test = 0.333):
	df = pd.read_json(open("train.json", "r"))

	df["num_photos"] = df["photos"].apply(len)
	df["num_features"] = df["features"].apply(len)
	df["num_description_words"] = df["description"].apply(lambda x: len(x.split(" ")))
	df["created"] = pd.to_datetime(df["created"])
	df["created_month"] = df["created"].dt.month
	df["created_day"] = df["created"].dt.day

	num_feats = ["bathrooms", "bedrooms", "latitude", "longitude", "price",
	             "num_photos", "num_features", "num_description_words",
	             "created_month", "created_day"]
	X = df[num_feats]
	y = df["interest_level"]


	def get_dist_sp(subset):
	  if(subset != -1):
	    subset_df = df.iloc[:subset]
	    coords = subset_df[['latitude','longitude']].to_numpy()
	  else:
	    coords = df[['latitude','longitude']].to_numpy()
	  distances = scipy.spatial.distance.pdist(coords, 'euclidean')
	  return scipy.spatial.distance.squareform(distances)

	def get_pos_dict(subset = -1):
	  if(subset >= 0):
	    subset_df = df.iloc[:subset]
	    pos = subset_df[['latitude','longitude']].to_numpy()
	  else:
	    pos = df[['latitude','longitude']].to_numpy()
	  coord_pairs = list(zip(list(pos[:,1]), list(pos[:,0])))
	  indices = np.arange(len(coord_pairs))
	  pos_dict = dict(list(zip(indices, coord_pairs)))
	  return pos_dict

	def fast_knn(k, dist_arr):
	  sorted_indices = np.argsort(dist_arr, axis=1)
	  adj = np.zeros_like(sorted_indices)
	  for i in range(adj.shape[0]):
	    for j in range(k + 1):
	      adj[i][sorted_indices[i,j]] = 1 
	  return adj

	def get_adj(k, subset, plot = False):
	  dist_arr = get_dist_sp(subset)
	  adj_mat = fast_knn(k, dist_arr)
	  if plot:
	    G = nx.from_numpy_matrix(adj_mat)
	    pos = get_pos_dict(subset)
	    nx.set_node_attributes(G, pos, 'Coordinates')
	    fig, ax = plt.subplots()
	    plt.title('Visualization of graph with nodes mapped on real coordinates.')
	    plt.ylabel('Latitude')
	    plt.xlabel('Longitude')
	    nx.draw_networkx(G, pos, node_size=10, with_labels=False, ax=ax)
	    ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)

	dist_arr = get_dist_sp(-1)
	adj = fast_knn(5, dist_arr)
	G = nx.from_numpy_matrix(adj)
	pos = get_pos_dict(-1)
	nx.set_node_attributes(G, pos, 'Coordinates')
	nx.draw(G, pos, node_size=10, with_labels=False)
	plt.show()
	X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=fraction_test)

	return X_train, X_val, y_train, y_val, G

preprocessing_graph_1()