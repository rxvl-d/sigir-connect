from flask import Flask
from flask.json import jsonify
from flask import request

import sparql_dataframe
import requests
from bs4 import BeautifulSoup


app = Flask(__name__)

proceedings_page = BeautifulSoup(requests.get('https://sigir.org/sigir2022/program/proceedings/').content)

all_presenters = set([a.get_text() for authorss in proceedings_page.select('.DLauthors') for a in authorss.select('li')])
makg_endpoint = "https://makg.org/sparql"

def get_collaborators(author):
    q = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX magc: <https://makg.org/class/>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX fabio: <http://purl.org/spar/fabio/>
    PREFIX prism: <http://prismstandard.org/namespaces/basic/2.0/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT distinct ?paperTitle ?collaboratorName
    WHERE {
    ?paper rdf:type magc:Paper .
    ?paper dcterms:title ?paperTitle .
    ?paper dcterms:creator ?collaborator .
    ?paper dcterms:creator ?author .
    ?collaborator rdf:type magc:Author .
    ?collaborator foaf:name ?collaboratorName .
    ?author rdf:type magc:Author .
    ?author foaf:name """ + '"' + author + '"'  + """^^xsd:string .
    }"""

    df = sparql_dataframe.get(makg_endpoint, q)
    df = df[df.collaboratorName.isin(all_presenters)]
    return dict(df.values)

@app.route("/")
def hello_world():
        return """
        <p>Hey, welcome to SIGIR '22 Connect!</p>
        Enter the name of a researcher here and I'll return conference attendees who have collaborated with them.
 <form action="/search" method="GET">
  <label for="name">Name:</label><br>
  <input type="text" id="name" name="name" value="John"><br>
  <input type="submit" value="Submit">
</form> 
        """

@app.route("/search")
def search():
    out = get_collaborators(request.args.get('name'))
    if out:
	    return jsonify(out)
    else:
        return 'Author not found. Try capitalizing and checking the spelling. It should match the author name in the MAGK: https://link.springer.com/chapter/10.1007/978-3-030-30796-7_8'
