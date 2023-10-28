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
from bs4 import BeautifulSoup as bs


def save_df(df_to_append, path, header):
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




datos = pd.read_csv(sys.argv[1]) #movies = pd.read_csv("data/all_the_movies.csv")
path_movies = sys.argv[2] #path_movies = "data/movies_1.csv"
path_genres = sys.argv[3] #path_genres = "data/genres_1.csv"
path_dir = sys.argv[4] #path_dir = "data/dir_1.csv"
path_prod = sys.argv[5] #path_prod = "data/prod_1.csv"

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
 
        movie_link = "https://letterboxd.com" + datos["movie_link"][i] 

        print(movie_link)
        
        #tengo que ver todas sus páginas
            
        for attempt in range(3):
            try:
                r = requests.get(movie_link, allow_redirects="False", headers=headers)
                break
            
            except requests.exceptions.ChunkedEncodingError:
                time.sleep(1)
    

        # si la respuesta no es 200: chau
        if r.status_code != 200:
            pass

        tree = lxml.html.fromstring(r.text)
        
        #para las img
        soup = bs(r.text)
        script_w_data = soup.select_one('script[type="application/ld+json"]')
        json_obj = json.loads(script_w_data.text.split(' */')[1].split('/* ]]>')[0])

        #movies metadata
        
        title = [element.text for element in tree.xpath('//*[@id="featured-film-header"]/h1')]
        year = [element.text for element in tree.xpath('//*[@id="featured-film-header"]/p/small/a')]
        if len(year) == 0:
            year = "-1"

        description = [' '.join([element.text for element in tree.xpath('//*[@id="film-page-wrapper"]/div[2]/section[2]/section/div[1]/div/p')])]
        
        if "image" in json_obj:
            image_link = [json_obj['image']]
        else:
            image_link = "https://s.ltrbxd.com/static/img/empty-poster-230.876e6b8e.png"


        #stats
        stats = requests.get(f"https://letterboxd.com/esi{datos.movie_link[i]}stats/")
        stats_tree = lxml.html.fromstring(stats.text)

        #vars
        watched_by = [element.text for element in stats_tree.xpath('//*[@class="stat filmstat-watches"]/a')]
        liked_by = [element.text for element in stats_tree.xpath('//*[@class="stat filmstat-likes"]/a')]
        appears_in_lists = [element.text for element in stats_tree.xpath('//*[@class="stat filmstat-lists"]/a')]


        #stats histogram
        try:
            url_ = datos["movie_link"][i]
            url_get = f"https://letterboxd.com/csi{url_}rating-histogram/"
            stats_histogram = requests.get(url_get)
            stats_histogram_tree = lxml.html.fromstring(stats_histogram.text)
            avg_rating = [element.text for element in stats_histogram_tree.xpath('//*[contains(@class,"display-rating")]')]
            if len(avg_rating) == 0:
                avg_rating="-1"

        except:
            avg_rating="-1"

        dict_to_append = {'movie_link': movie_link,
            'title': title,
            'image_link':image_link,
            'year': year,
            'description': description,
            'watched_by': watched_by,
            'liked_by': liked_by,
            'appears_in_lists': appears_in_lists,
            'avg_rating': avg_rating
            }

        #armo el dataframe
        df_to_append = pd.DataFrame()
        df_to_append = pd.DataFrame(dict_to_append)

        #header del csv
        header = dict_to_append.keys()

        save_df(df_to_append, path_movies, header)


        genres_link = [element.attrib["href"] for element in tree.xpath('//*[@id="tab-genres"]/div/p/a')]
        genres = [element.text for element in tree.xpath('//*[@id="tab-genres"]/div/p/a')]
        movie_link_ = [movie_link]*len(genres_link)

        dict_to_append = {'movie_link_': movie_link_,
            'genres': genres,
            'genres_link': genres_link
            }
        
         #armo el dataframe
        df_to_append = pd.DataFrame()
        df_to_append = pd.DataFrame(dict_to_append)

        #header del csv
        header = dict_to_append.keys()

        save_df(df_to_append, path_genres, header)


        #df de directores
        director = [element.text for element in tree.xpath('//*[@id="tab-crew"]/div/p/a')]
        director_link = [element.attrib["href"] for element in tree.xpath('//*[@id="tab-crew"]/div/p/a')]
        movie_link_ = [movie_link]*len(director_link)

        dict_to_append = {'movie_link': movie_link,
            'director': director,
            'director_link': director_link,
            }
        
        #armo el dataframe
        df_to_append = pd.DataFrame()
        df_to_append = pd.DataFrame(dict_to_append)

         #header del csv
        header = dict_to_append.keys()
        save_df(df_to_append, path_dir, header)


        #df de productoras
        if "productionCompany" in json_obj:
            productor_type = [production["@type"] for production in json_obj["productionCompany"]]
            productor_name = [production["name"] for production in json_obj["productionCompany"]]
            productor_link = [production["sameAs"] for production in json_obj["productionCompany"]]
            movie_link_ = [movie_link] * len(productor_link)

            dict_to_append = {'movie_link': movie_link,
                'productor_type': productor_type,
                'productor_name': productor_name,
                'productor_link': productor_link
                }

            #armo el dataframe
            df_to_append = pd.DataFrame()
            df_to_append = pd.DataFrame(dict_to_append)
        
            #header del csv
            header = dict_to_append.keys()
            save_df(df_to_append, path_prod, header)
            

 
    # si todo falla, chau
    except Exception as e:
        print(e)
        #pass        
        pass