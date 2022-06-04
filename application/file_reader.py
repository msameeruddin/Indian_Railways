import os
import json

import geopandas as gpd
import numpy as np
import pandas as pd

data_path = '\\'.join(os.getcwd().split('\\')[:-1]) + '\\data\\'
json_files_path = data_path + 'json_files\\'
csv_files_path = data_path + 'csv_files\\'
shp_files_path = data_path + 'shape_files'

# Read JSON files
def read_json_file(file_name, data_path=json_files_path):
    if not data_path.endswith('\\'):
        data_path = data_path + '\\'

    file_path = data_path + file_name
    if os.path.isfile(path=file_path):
        with open(file=file_path, mode='r', encoding='utf-8') as fjson:
            data = json.load(fp=fjson)
    else:
        print('Invalid path specified.')
        data = {}
    
    return data


# Read SHP files
def read_shp_file(dir_name, data_path=shp_files_path):
    if not data_path.endswith('\\'):
        data_path = data_path + '\\'

    dir_path = data_path + dir_name
    if os.path.isdir(s=dir_path):
        gdf = gpd.read_file(filename=dir_path)
    else:
        print('Invalid path specified.')
        gdf = [None]
    
    return gdf


# Read CSV files
def read_csv_file(file_name, data_path=csv_files_path):
    if not data_path.endswith('\\'):
        data_path = data_path + '\\'
    
    file_path = data_path + file_name
    if os.path.isfile(path=file_path):
        df = pd.read_csv(filepath_or_buffer=file_path)
    else:
        print('Invalid path specified.')
        df = [None]
    
    return df