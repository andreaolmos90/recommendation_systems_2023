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


datos = pd.read_csv(sys.argv[1]) #movies = pd.read_csv("data/all_the_movies.csv")
path_movies = sys.argv[2] #path_movies = "data/movies_1.csv"
path_genres = sys.argv[3] #path_genres = "data/genres_1.csv"

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


        #tengo que ver todas sus páginas
            
        for attempt in range(3):
            try:
                r = requests.get(movie_link, allow_redirects="False", headers=headers)
                break
            
            except requests.exceptions.ChunkedEncodingError:
                time.sleep(1)
    
        print("request done")
        print(r.status_code)

        # si la respuesta no es 200: chau
        if r.status_code != 200:
            break

        tree = lxml.html.fromstring(r.text)
        
        #para las img
        soup = bs(r.text)
        script_w_data = soup.select_one('script[type="application/ld+json"]')
        json_obj = json.loads(script_w_data.text.split(' */')[1].split('/* ]]>')[0])

        #movies metadata
        
        title = [element.text for element in tree.xpath('//*[@id="featured-film-header"]/h1')]
        director = [element.text for element in tree.xpath('//*[@id="featured-film-header"]/p/a/span')]
        director_link = [element.attrib["href"] for element in tree.xpath('//*[@id="featured-film-header"]/p/a')]
        year = [element.text for element in tree.xpath('//*[@id="featured-film-header"]/p/small/a')]
        description = [element.text for element in tree.xpath('//*[@id="film-page-wrapper"]/div[2]/section[2]/section/div[1]/div/p')]
        image_link = json_obj['image']

        #stats
        stats = requests.get(f"https://letterboxd.com/esi{datos.movie_link[i]}stats/")
        stats_tree = lxml.html.fromstring(stats.text)

        #vars
        watched_by = [element.text for element in stats_tree.xpath('//*[@class="stat filmstat-watches"]/a')]
        liked_by = [element.text for element in stats_tree.xpath('//*[@class="stat filmstat-likes"]/a')]
        appears_in_lists = [element.text for element in stats_tree.xpath('//*[@class="stat filmstat-lists"]/a')]


        #stats histogram
        stats_histogram = requests.get(f"https://letterboxd.com/csi{datos.movie_link[i]}rating-histogram/")
        stats_histogram_tree = lxml.html.fromstring(stats_histogram.text)

        #vars
        avg_rating = [element.text for element in stats_histogram_tree.xpath('//*[@class="tooltip display-rating -highlight"]')]


        dict_to_append = {'movie_link': movie_link,
            'title': title,
            'image_link':image_link,
            'director': director,
            'director_link': director_link,
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

        # si no existe el csv, se crea con el header
        if os.path.isfile(path_genres)==False:
            with open(path_genres, 'a') as f:
                writer = csv.writer(f)
                writer.writerow(header)
                df_to_append.to_csv(f, header=False, index=False)
                f.flush()

        # si existe el csv, se appendea el dataframe
        else:
            with open(path_genres, 'a') as f:
                df_to_append.to_csv(f, header=False, index=False)
                f.flush()

        print("genres data saved")

    # si todo falla, chau
    except:
        pass        