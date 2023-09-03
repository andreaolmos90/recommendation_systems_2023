import requests
import lxml
from lxml import etree
from lxml import html
import xml.etree.ElementTree as ET
import pandas as pd
import os
from pathlib import Path
import csv
import sys

path_list = sys.argv[1] #"data/lists.csv"

users = sys.argv[2] #"data/users_1.csv"

#importar datos de usuarios
users = pd.read_csv(users)
print(users.head())