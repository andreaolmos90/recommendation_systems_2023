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

datos = pd.read_csv(sys.argv[1]) #listas = pd.read_csv("data/lists.csv")
path_movies = sys.argv[2] #path_movies = "data/movies_lists_1.csv"
path_lists = sys.argv[3] #path_lists = "data/lists_data_1.csv"


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
    
    if i % 100 == 0:
        time.sleep(10)

    list_link = "https://letterboxd.com" + datos["list_link"][i] + "detail/page/"
    list_id = datos["list_id"][i]

    #tengo que ver todas sus páginas
    for number in range(1, 10000):
        r = requests.get(f"{list_link}{number}", allow_redirects=False)
        print("request done")
        print(r.status_code)
        
        if r.status_code == 200:
            tree = lxml.html.fromstring(r.text)
            table = tree.xpath('//*[@id="content"]/div/div/section/ul')
            
            #si la página tiene contenido
            if(len(table)) != 0:
                    
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

                        
                if len(table[0].findall("li")) != 0:
                    
                #films data
                    list_id_arr = [list_id] * len(table[0].findall("li"))
                        
                    #movie_id = list(set([element.attrib["data-film-id"] for element in table[0].findall(".//*[@data-film-id]")]))

                    movie_link = [element.attrib["href"] for element in table[0].findall(".//*[@class='headline-2 prettify']/a")]
        
                    #movie_stars = [element.text for element in table[0].findall(".//*[@class='film-detail-meta rating-green']/span")]
                    #print((movie_stars))
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

                else:
                    break 
        
        else:
            break