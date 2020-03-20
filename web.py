from flask import Flask , jsonify
app = Flask(__name__)

all_services ={"result":[{"id":0 , "name":"bubble_sort"},{ "id":1 , "name":"merge_sort"}]}


@app.route('/')
def index():
  return "Hello world "
  
@app.route('/api/getAllServices')
def getAllservices():
  return jsonify(all_services)
  
app.run(port=5000)

