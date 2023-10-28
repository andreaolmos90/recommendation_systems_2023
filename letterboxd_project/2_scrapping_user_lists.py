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

path = sys.argv[1] #"data/lists.csv"
users = sys.argv[2] #"data/users.csv"

#importar datos de usuarios
users = pd.read_csv(users)

users_list_links = "https://letterboxd.com" + users.user_lists_link + "page/"


#para cada usuario
for user in users_list_links:
    #tengo que ver todas sus páginas
    for number in range(1, 10000):
        r = requests.get(f"{user}{number}")
        tree = lxml.html.fromstring(r.text)
        table = tree.xpath('//*[@id="content"]/div/div/section/section')
        if(len(table)==0):
            break

        if len(table[0].findall(".//*[@class='list -overlapped -summary ']")) != 0:
            
            list_link = [element.attrib["href"] for element in table[0].findall(".//*[@class='list-link']")]
            list_id = [element.attrib['data-film-list-id'] for element in table[0].findall(".//*[@class='list -overlapped -summary ']")]
            user_id = [element.attrib['data-person'] for element in table[0].findall(".//*[@class='list -overlapped -summary ']")]
            list_extension = [element.text for element in table[0].findall(".//*[@class='value']")]
        
            #armo el dataframe
            df_to_append = pd.DataFrame()
            df_to_append = pd.DataFrame(
                {'user_id': user_id,
                'list_id': list_id,
                'list_link': list_link,
                'list_extension': list_extension
                })

            #header del csv
            header = ["user_id", "list_id", "list_link", "list_extension"]

            # si no existe el csv, se crea con el header
            if os.path.isfile(path)==False:
                with open(path, 'a') as f:
                    writer = csv.writer(f)
                    writer.writerow(header)
                    df_to_append.to_csv(f, header=False, index=False)
                    f.flush()

            # si existe el csv, se appendea el dataframe
            else:
                with open(path, 'a') as f:
                    df_to_append.to_csv(f, header=False, index=False)
                    f.flush()

        else:
            break  