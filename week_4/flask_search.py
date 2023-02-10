from flask import Flask, render_template, request

# With this import we can access the functions from search_engine_week4.py
import search_engine_week4 as se

#Initialize Flask instance
app = Flask(__name__)

print("Loading articles")
documents = se.index_documents_from_text_file("articles.txt")
if len(documents) == 100:
    print("Successfully loaded articles")


# The rest of the code is copied from the example

@app.route('/')
def index():
   return render_template("welcome_page.html")

@app.route('/options')
def optionts():
    return render_template("options.html")
#Function search() is associated with the address base URL + "/search"

@app.route('/boolean')
def search_b():

    #Get query from URL variable
    #query = request.args.get('query')

    #Initialize list of matches
    #matches = []

    #If query exists (i.e. is not None)
    #if query:
        #Look at each entry in the example data
        #for entry in example_data:
            #If an entry name contains the query, add the entry to matches
            #if query.lower() in entry['name'].lower():
                #matches.append(entry)

    #Render index.html with matches variable
    return render_template('boolean.html') #matches=matches)

@app.route('/td_idf')
def search_t():
    return render_template('td_idf.html') #matches=matches)


