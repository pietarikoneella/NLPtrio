from flask import Flask, render_template, request, redirect, url_for
import re
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import spacy
import pke
import movie_search_functions as ms
from movies import *

import itertools

app = Flask(__name__)

synopsis_list = ms.index_documents_from_text_file()
synopsis_list_bold = []
stemmed_synopsis_list = ms.stemming_documents(synopsis_list)

file = open("movies.txt", "r", encoding = "ISO-8859-1")
ranks = file.readline().split("#")
del ranks[-1] # remove "\n"
titles = file.readline().split("#")
del titles[-1]
years = file.readline().split("#")
del years[-1]
ratings = file.readline().split("#")
del ratings[-1]
summaries = file.readline().split("#")
del summaries[-1]
file.close()

file = open("imdb_photos.txt", "r")
photos = file.readline().split("#")
file.close()

theme = [] # one score and keyphrase
ten_themes = [] # themes for one movie
themes = [] # list of lists of 10 themes
file = open("synopsis_themes.txt", "r", encoding= 'utf-8')
for i in range(250):
    for i in range(10):
        theme = file.readline().split(" ", 1) # list of score and keyphrase
        try: # this try/except block is needed because one movie has just 7 themes
            theme[0] = float(theme[0])  # convert score into float
        except:
            break
        theme[1] = re.sub(r"\n", r"", theme[1]) # remove newline from keyphrase
        ten_themes.append(theme)
    themes.append(ten_themes)
    ten_themes = []
    space = file.readline() # skip the empty lines
file.close()

file = open("synopses.txt", "r", encoding= 'Windows-1252')
synopses = file.read()
synopses = re.sub(r"<synopsis>", "", synopses)
synopses = synopses.split("</synopsis>")
del synopses[-1] # remove newlines
file.close()

data = zip(titles, ratings, years, themes, summaries, synopses, photos) 
query = ""
result_list = []
movie_list = []    

i = 0
for item in data:
    # New movie object Movie(id, title, rating, year, themes, summary, synopsis, photos)
    new_movie = Movie(i, item[0], item[1], item[2], item[3], item[4], item[5], item[6])
    movie_list.append(new_movie)
    i+=1

@app.route('/')
def index():
    return redirect('index')


@app.route('/index')
def search():
    """ This function now goes through the data and makes a result list
        out of it if and only if the user has typed in a query.
        Then it uses the query to get relevant search results
    """
    query = request.args.get('query')
    method = request.args.get('search_method')
    
    
    i = 0
    doc_ids = []
    result_ids = []
    final_result_list = []
    s_new = []
    stemmed_query = ""

    #This is done here to remove highlights from earlier searches
    for i in range(250):
        movie_list[i].set_synopsis(synopses[i])

    if query:
        #Exact matches
        if '"' in query:
            if method == 'Boolean':
                query = re.sub(r"\"", r"", query)
                result_ids = ms.search_b(synopsis_list, query)        
                final_result_list = []
                if len(result_ids) > 0:
                    for i in result_ids:
                        final_result_list.append(movie_list[i])

            elif method == 'tf-idf':
                result_ids = ms.search_t(synopsis_list, query)
                final_result_list = []
                if len(result_ids) > 0:
                    for i in result_ids:
                        final_result_list.append(movie_list[i])

            #Highlighting query words
            for id in result_ids:
                    s = movie_list[id].get_synopsis()
                    parts = []
                    if method == 'Boolean':
                        parts0 = re.split(r'\band\b|\bor\b|\bnot\b|\"', query)
                    elif method == 'tf-idf':
                        parts0 = re.split(r'\"', query)
                    for part in parts0:
                        if part != "" and part != " ":
                            parts.append(part.strip())
            
                    queries = []
                    for part in parts:
                        if part != "or" and part != "and" and part != "not":
                            list_of_lists = []
                            for token in part.split():
                                list_of_lists.append([token[0].lower() + token[1:], token[0].upper() + token[1:]])

                            # get all combinations of lowercase and uppercase words
                            combinations = list(itertools.product(*list_of_lists))
                            for i in combinations:
                                queries.append(" ".join(i))
        
                    s_new = s[:]
                    for q in queries:    
                        s_new = re.sub("\\b"+str(q)+"\\b", f"<mark><b> {q} </b></mark>", s_new)
                        movie_list[id].set_synopsis(s_new)
        
        # Stem search
        elif '"' not in query:                
            stemmed_query = ms.stem_query(query)
            if method == 'Boolean':
                result_ids = ms.search_b(stemmed_synopsis_list, stemmed_query)        
                final_result_list = []
                if len(result_ids) > 0:
                    for i in result_ids:
                        final_result_list.append(movie_list[i])

            elif method == 'tf-idf':
                result_ids = ms.search_t(stemmed_synopsis_list, stemmed_query)
                final_result_list = []
                if len(result_ids) > 0:
                    for i in result_ids:
                        final_result_list.append(movie_list[i])

            #Highlighting query words
            for id in result_ids:
                    s = movie_list[id].get_synopsis()
                    
                    parts_1 = []
                    if method == 'Boolean':
                        parts_1_0 = re.split(r'\band\b|\bor\b|\bnot\b|\"', stemmed_query)
                    elif method == 'tf-idf':
                        parts_1_0 = stemmed_query.split()
                    for part in parts_1_0:
                        if part != "" and part != " ":
                            parts_1.append(part.strip())
                    parts_2 = []
                    if method == 'Boolean':
                        parts_2_0 = re.split(r'\band\b|\bor\b|\bnot\b|\"', query)
                    elif method == 'tf-idf':
                        parts_2_0 = query.split()
                    for part in parts_2_0:
                        if part != "" and part != " ":
                            parts_2.append(part.strip())
                    parts = parts_1 + parts_2
            
                    queries = []
                    for part in parts:
                        if part != "or" and part != "and" and part != "not":
                            list_of_lists = []
                            for token in part.split():
                                list_of_lists.append([token[0].lower() + token[1:], token[0].upper() + token[1:]])

                            # get all combinations of lowercase and uppercase words
                            combinations = list(itertools.product(*list_of_lists))
                            for i in combinations:
                                queries.append(" ".join(i))
        
                    s_new = s[:]
                    for q in queries:    
                        s_new = re.sub("\\b"+str(q), f"<mark><b> {q} </b></mark>", s_new)
                        movie_list[id].set_synopsis(s_new)

                
    else:
        if method == 'Boolean' or method == 'td-idf':
            pass
        elif method == 'List all movies':
            final_result_list = movie_list[:]

        else:
            pass

    if query:
        print('The query is "' + query +'".')

    number=len(final_result_list)

    return render_template('index.html',  movie_list=movie_list, final_result_list=final_result_list, number=number, query=query, method=method)


@app.route('/movie/<title>/<id>')

def show_movie(title, id):
    """ This function creates a page for an individual movie object.
        Theme extraction and later on adding a plot is done here - only if
        the user clicks the link for that particular movie.
    """
    id = int(id)

    movie_ = Movie(id, titles[id], ratings[id], years[id], themes[id], summaries[id], synopses[id], photos[id][1:(len(photos[id])-2)])
    title = movie_.get_title()

    #ms.make_plot(movie_.get_themes(), movie_.get_title())
    ms.make_bubble_plot(movie_.get_themes(), movie_.get_title())

    return render_template('movie.html', result_list=result_list, id=id, query=query, title=title, movie_=movie_)
