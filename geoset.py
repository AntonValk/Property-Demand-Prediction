import geopandas as gpd
from geopandas import GeoSeries
from shapely.geometry import Polygon
import shapely.geometry as geoms
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt 
from preprocess import preprocess_data_geog
from sklearn.model_selection import train_test_split



df = preprocess_data_geog()


nybb_path = gpd.datasets.get_path('nybb')
boros = gpd.read_file(nybb_path)
boros.set_index('BoroCode', inplace=True)
boros.sort_index(inplace=True)
# print(boros.crs)
boros = boros.to_crs(epsg=4326)
print(boros.head())
boros.plot()
plt.show()


geos = gpd.GeoSeries(df[['longitude', 'latitude']]\
            .apply(lambda x: geoms.Point((x.longitude, x.latitude)), axis=1), \
            crs={'init': 'epsg:4326'})
# geos = geos.to_crs(epsg=2263)

# geos = gpd.GeoDataFrame(geos, geometry=gpd.points_from_xy(geos.longitude, geos.latitude))

gdf = gpd.GeoDataFrame(df, geometry=geos)


print(geos)

geos.plot()
plt.show()

# db['geometry'] = geos
# db = gpd.GeoDataFrame.from_records(db)
# db.crs = geos.crs

# only keep nyc 
in_nyc = gpd.sjoin(gdf, boros, how="inner", op='intersects')
# in_nyc = boros.contains(geos)

nyc = pd.DataFrame(in_nyc)

num_feats = ["bathrooms", "bedrooms", "latitude", "longitude", "price",
             "num_photos", "num_features", "num_description_words",
             "created_month", "created_day", "BoroName"]
X = nyc[num_feats]
y = nyc["interest_level"]

# print(list(in_nyc))
# print(in_nyc['BoroName'])

print(X['BoroName'].value_counts())

pd.DataFrame.to_csv(nyc)

X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.33)

print(X_train.shape, y_train.shape)