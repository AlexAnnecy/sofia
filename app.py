import os
import uuid

import openai
from flask import Flask, redirect, render_template, request, url_for

from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Replace the connection string and table name with your own Azure Table Storage connection string and table name
connection_string = os.getenv("AZURE_DB_CONNECTION_STRING")
table_name = 'URLS'
table_service = TableService(connection_string=connection_string)

@app.route('/add_url', methods=['POST'])
def add_url():
	url = request.form['url']

	# Create an Entity object and add the URL to it
	entity = Entity()
	entity.PartitionKey = 'urls'
	entity.RowKey = str(uuid.uuid4())
	entity.url = url
	table_service.insert_entity(table_name, entity)
	
	return "URL added successfully!"

@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        animal = request.form["animal"]
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=generate_prompt(animal),
            temperature=0.6,
        )
        return redirect(url_for("index", result=response.choices[0].text))

    result = request.args.get("result")
    return render_template("index.html", result=result)


def generate_prompt(animal):
    return """Suggest three names for an animal that is a superhero.

Animal: Cat
Names: Captain Sharpclaw, Agent Fluffball, The Incredible Feline
Animal: Dog
Names: Ruff the Protector, Wonder Canine, Sir Barks-a-Lot
Animal: {}
Names:""".format(
        animal.capitalize()
    )
