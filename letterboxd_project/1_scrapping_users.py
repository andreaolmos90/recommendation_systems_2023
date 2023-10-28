import requests
import lxml
from lxml import etree
from lxml import html
import xml.etree.ElementTree as ET
import pandas as pd
import os
from pathlib import Path
import csv
import random
import json
from bs4 import BeautifulSoup as bs


path = "data/users.csv"
file = "users.csv"

for number in range(1,1000):
    r = requests.get(f"https://letterboxd.com/members/popular/this/week/page/{number}/")
    tree = lxml.html.fromstring(r.text)
    table = tree.xpath('//*[@id="content"]/div/div/section/table/tbody')
    
    # si la tabla no está vacía de filas
    if len(table[0].findall("tr")) != 0:
        # guardo las variables
        user_link = [element.attrib["href"] for element in table[0].findall(".//*[@class='title-3']/a")]
        user_lists_link = [element.attrib["href"] for element in table[0].findall(".//*[@class='has-icon icon-16 icon-list']")]
        user_watched_num = [int(element.text.replace(",", "")) for element in table[0].findall(".//*[@class='has-icon icon-16 icon-watched']")]
        user_lists_num = [int(element.text.replace(",", "")) for element in table[0].findall(".//*[@class='has-icon icon-16 icon-list']")]
        user_likes_num = [int(element.text.replace(",", "")) for element in table[0].findall(".//*[@class='has-icon icon-16 icon-liked']")]
        
        #armo el dataframe
        df_to_append = pd.DataFrame()
        df_to_append = pd.DataFrame(
            {'user_link': user_link,
            'user_lists_link': user_lists_link,
            'user_watched_num': user_watched_num,
            'user_lists_num': user_lists_num,
            'user_likes_num': user_likes_num
            })
        #header del csv
        header = ["user_link", "user_lists_link", "user_watched_num", "user_lists_num", "user_likes_num"]
        
        # si no existe el csv, se crea con el header
        if os.path.isfile(path)==False:
            with open(file, 'a') as f:
                writer = csv.writer(f)
                writer.writerow(header)
                df_to_append.to_csv(f, header=False, index=False)
                f.flush()
        
        # si existe el csv, se appendea el dataframe
        else:
            with open(file, 'a') as f:
                df_to_append.to_csv(f, header=False, index=False)
                f.flush()
    
    else:
        break