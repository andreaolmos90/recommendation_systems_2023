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
import time
import json
import random

datos = pd.read_csv(sys.argv[1]) #listas = pd.read_csv("data/lists.csv")
path_movies = sys.argv[2] #path_movies = "data/movies_lists.csv"
path_lists = sys.argv[3] #path_lists = "data/lists_data.csv"


#dictionary for stars
stars_interpreter = {
    "-" : -1,
    " ½ ": 0.5,
    " ★ " : 1,
    " ★½ " : 1.5,
    " ★★ " : 2,
    " ★★½ " : 2.5,
    " ★★★ " : 3,
    " ★★★½ " : 3.5, 
    " ★★★★ " : 4,
    " ★★★★½ " : 4.5,
     " ★★★★★ ": 5
}




#para cada lista del archivo de listas
for i in range(0, len(datos)):
    
    try: 
        user_agent_list = [
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
        "Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10.5; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15"
        ]


        headers = {
            'User-Agent':'Mozilla/5.0',
            'Content-Type':'application/json',
            'method':'GET',
            'Accept':'application/vnd.github.cloak-preview'
        }

        headers['User-Agent'] = random.choice(user_agent_list)
        
        list_link = "https://letterboxd.com" + datos["list_link"][i] + "detail/page/"
        list_id = datos["list_id"][i]

        #tengo que ver todas sus páginas
        for number in range(1, 10000):
            
            for attempt in range(3):
                try:
                    r = requests.get(f"{list_link}{number}", allow_redirects="False", headers=headers)
                    break
                
                except requests.exceptions.ChunkedEncodingError:
                    time.sleep(1)
        
            print("request done")
            print(r.status_code)

            # si la respuesta no es 200: chau
            if r.status_code != 200:
                break

            tree = lxml.html.fromstring(r.text)
            table = tree.xpath('//*[@id="content"]/div/div/section/ul')
            
            #si la página no tiene contenido: chau
            if(len(table)) == 0:
                print("la tabla no tiene contenido")
                break
            
            #si es la página 1, guardo data de la lista
            if number == 1:
                #list data
                list_title = [title.text for title in tree.xpath('//*[@id="content"]/div/div/section/div[2]/h1')]
                list_description = ' '.join([str(element.text) for element in tree.xpath('//*[@id="content"]/div/div/section/div[2]/div/p')])
                #get list likes
                r = requests.get(f"https://letterboxd.com/ajax/letterboxd-metadata/?likeables=filmlist%3A{list_id}&likeCounts=filmlist%3A{list_id}")
                list_likes = json.loads(r.text)["likeables"][0]["count"]

                #armo el dataframe
                df_to_append = pd.DataFrame()
                df_to_append = pd.DataFrame(
                    {'list_id': list_id,
                    'list_title': list_title,
                    'list_description': list_description,
                    'list_likes': list_likes
                    })

                #header del csv
                header = ["list_id","list_title", "list_description", "list_likes"]

                # si no existe el csv, se crea con el header
                if os.path.isfile(path_lists)==False:
                    with open(path_lists, 'a') as f:
                        writer = csv.writer(f)
                        writer.writerow(header)
                        df_to_append.to_csv(f, header=False, index=False)
                        f.flush()

                # si existe el csv, se appendea el dataframe
                else:
                    with open(path_lists, 'a') as f:
                        df_to_append.to_csv(f, header=False, index=False)
                        f.flush()

                print("list data saved")

            # si la tabla no tiene películas, chau 
            if len(table[0].findall("li")) == 0:
                print("la tabla no tiene películas")
                break
                
            #films data
            list_id_arr = [list_id] * len(table[0].findall("li"))
            movie_link = [element.attrib["href"] for element in table[0].findall(".//*[@class='headline-2 prettify']/a")]
            details = [element for element in table[0].findall(".//*[@class='film-detail-content']")]

            movie_stars = []
    
            for calif in details:
                    
                    try:
                        if calif[1].tag == "p":
                            movie_stars.append((calif[1][0].text))
                        else:
                            movie_stars.append("-")

                    except:
                        movie_stars.append("-")


            movie_calification = [stars_interpreter[x] for x in movie_stars]
            movie_position = [element.text for element in table[0].findall(".//*[@class='list-number']")] 

            if len(movie_position) == 0:
                movie_position = [0] * len(movie_link)


            #armo el dataframe
            df_to_append = pd.DataFrame()
            df_to_append = pd.DataFrame(
                {'list_id': list_id_arr,
                #'movie_id': movie_id,
                'movie_link': movie_link,
                'movie_stars': movie_stars,
                'movie_calification': movie_calification,
                'movie_position': movie_position
                })

            #header del csv
            header = ["list_id", "movie_link", "movie_stars", "movie_calification", "movie_position"]

            # si no existe el csv, se crea con el header
            if os.path.isfile(path_movies)==False:
                with open(path_movies, 'a') as f:
                    writer = csv.writer(f)
                    writer.writerow(header)
                    df_to_append.to_csv(f, header=False, index=False)
                    f.flush()

            # si existe el csv, se appendea el dataframe
            else:
                with open(path_movies, 'a') as f:
                    df_to_append.to_csv(f, header=False, index=False)
                    f.flush()

            print("movies data saved")
    
    # si todo falla, chau
    except:
        print("falló todo, chau")
        pass        