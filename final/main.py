import csv, requests
from flask import Flask, jsonify, request, redirect

app = Flask(__name__)

names = {}

@app.route("/")
def index():
    chars = request.args.get("chars", "")
    if chars:
        suggestion = request_suggestions(url_schema(request.url), chars)
        if suggestion:
            result = suggestion
        else: 
            result = "No suggestion found"
        url_accept = url_schema(request.url) + "accepted?"
        url_decline = url_schema(request.url) + "declined"
        return (
            readme() +
                """<form action=""" + url_decline + """ method="get">
                    <input name="name" value=""" + chars + """  >
                    <input type="hidden" type="text" name="suggestion" value=""" + result + """  >
                    <input type="hidden" type="text" name="url" value=""" + url_schema(request.url) + """  >
                    <input type="submit" value="Decline (write the full name you wanted)">
                </form>
                <b> Suggestion : """
                + result +
                """
                </b> <br/> <br/>
                <form action=""" + url_accept + """ method=get>
                    <input type="hidden" type="text" name="name" value=""" + result + """  >
                    <input type="hidden" type="text" name="url" value=""" + url_schema(request.url) + """  >
                    <input type="submit" value="Accept" />
                </form>
                """
        )
            
    else:
        return (
            readme() +
            """<form action="" method="get">
                    <input type="text" name="chars">
                    <input type="submit" value="Get suggestion">
                </form> """
        )
                

def request_suggestions(schema, chars):
    """
    Returns the first suggestion for the first characters given by the user.
    """
    url = schema + 'search?chars=' + chars.capitalize()
    response = requests.get(url).json()
    if response['content']:
        return str(response['content'][0])
    else:
        return None

@app.route("/search")
def get_suggestions():
    """
    Takes one parameter : chars, the first characters to use for the suggestion.
    It returns a json containing the set of suggestions, ordered by priority.
    """
    
    if not 'chars' in request.args:
        result = { 
            'type': '%s value is missing' % param, 
            'content': '', 
            'status': 'REQUEST_DENIED'
        }
        return jsonify(result)
    try:
        chars = str(request.args['chars'])
    except:
        return "chars should be a string"
    
    data = read_file()
    suggestions = filter_database(data, chars)
    result = { 
        'type': 'result', 
        'content': suggestions, 
        'status': 'REQUEST_OK'
    } 
    print(names)  
    return jsonify(result)

@app.route("/accepted", methods=['GET'])
def accepted():
    """
    Takes one parameter : name, the accepted suggestion
    It increases the pk value of this name.
    If a return url is provided, redirects to this url.
    """
    
    if not 'name' in request.args:
        return "Please enter the name parameter"
    try:
        name = str(request.args['name'])
    except:
        return "The name parameter should be a string"
    
    data = read_file()

    increase_pk(data, name)
    update_database(data)

    if 'url' in request.args:
        return f"<html><body><p>Database updated ! <br/> You will be redirected in 3 seconds</p><script>var timer = setTimeout(function() {{window.location='{ str(request.args['url']) }'}}, 3000);</script></body></html>" 
    else:
        result = { 
            'type': 'result', 
            'content': "DATABASE UPDATED", 
            'status': 'REQUEST_OK'
        }   
        return jsonify(result)

@app.route("/declined", methods=['POST', 'GET'])
def declined():
    """
    Takes two parameters : 
    - suggestion, the declined suggestion
    - name, the name the user wanted
    It decreases the pk value of the declined suggestion.
    If the wanted name, is not in the database, it adds it.
    If the wanted name was in the database, it increases its pk value.
    
    Finally, it redirects to the home page.
    """
    for param in ['name', 'suggestion']:
        if not param in request.args:
            return "Please enter the name and suggestion parameters"
    try:
        name = str(request.args['name']).capitalize()
        suggestion = str(request.args['suggestion'])
    except:
        return "The name and suggestion parameters should be strings"
    
    data = read_file()

    if suggestion != 'No suggestion found':
        decrease_pk(data, suggestion)
    if name in data.keys():
            increase_pk(data, name)
    else:
        new_name(data, name)

    update_database(data)

    if 'url' in request.args:
        return f"<html><body><p>Database updated ! <br/> You will be redirected in 3 seconds</p><script>var timer = setTimeout(function() {{window.location='{ str(request.args['url']) }'}}, 3000);</script></body></html>" 
    else:
        result = { 
            'type': 'result', 
            'content': "DATABASE UPDATED", 
            'status': 'REQUEST_OK'
        }   
        return jsonify(result)

def url_schema(url):
    return url.split('?')[0]

def readme():
    """
    Returns the READ.ME for the index.
    """
    return """
        <h1> Hello, world ! </h1>
        This page is <b> an example of how to use my auto-fill system</b>. <br/>
        <i> You can refer to the READ.ME on my submission (github) to see how to do a request without this page. </i> <br/> <br/>
        By taking the first letters of your name on the form below,
        this page will request the suggestions to the system. <br/> <br/>
        It will then print the <b>first suggestion</b> in the <b>JSON format</b> that was returned after the request. <br/> <br/>
        You will then have to either accept the suggestion, or decline <b>by writting the name you wanted</b>. <br/> <br/>
        Each time you use the system, it should get better ! <br/> <br/>

        
    """

def print_database():
    """
    with open('database.csv', newline='') as csvfile:
        data = csv.DictReader(csvfile)
        for row in data:
            print(row['Name'], row['Pk'])
    """
    print(names)

def read_file():
    """
    Reads the initial database and returns a corresponding dictionnary.
    """
    if not names :
        with open('database.csv', newline='') as csvfile:
            data = csv.DictReader(csvfile)
            for row in data:
                names[row['Name']] = float(row['Pk'])
    return names

def update_database(data):
    """
    Updates the database according to a given dictionnary.
    
    clean_data = {suggestion: priority for suggestion, priority in data.items() if priority > 0.2}

    file = open('database.csv', 'w', newline='')
    writer = csv.writer(file)
    writer.writerow(['Name','Pk'])
    for k,v in clean_data.items():
        row = [k, v]
        writer.writerow(row)
    file.close()
    """
    names = data
    print("DEBUG -- DATABASE UPDATED :")
    print_database()

def new_name(data, name):
    """
    Add new name to the database
    """
    data[name.capitalize()] = 0.5

def filter_database(data, first_caracters):
    """
    Returns the list of suggestions in the database that have the same first caracters,
    sorted by priority
    """
    suggestions = {suggestion: priority for suggestion, priority in data.items() if suggestion.startswith(first_caracters)}
    return sorted([suggestion for suggestion, priority in data.items() if suggestion.startswith(first_caracters)], key = lambda x: data[x], reverse = True)

def increase_pk(data, name):
    pk_new = 0.6
    pk_star = data[name] + (1-data[name]) * pk_new

    data[name] = pk_star

def decrease_pk(data, name):
    pk_new = 0.8
    pk_star = data[name] - (1-data[name]) * pk_new

    data[name] = pk_star

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
    
