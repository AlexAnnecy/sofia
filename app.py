import os
import uuid

import openai
from flask import Flask, redirect, render_template, request, url_for

from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity
import filters
import requests

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

# tmp_url = "https://arstechnica.com/tech-policy/2023/02/starlinks-global-roaming-promises-worldwide-access-for-200-a-month/"
# art_title, art_content = filters.get_article(tmp_url)
# print(art_title)

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

    art_title, art_content = filters.get_article(url)
    summary = filters.summarize_text(art_content)

    return f"URL added successfully!\n {art_title} \n {summary}"

@app.route('/get_content', methods=['POST'])
def get_content():
    url = request.form['url']

    main_content = filters.extract_main_content(url)

    return f"Main content: {main_content}"

@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    url = request.form['url']
    response = requests.get(url)

    # Check if the response was successful
    if response.status_code != 200:
        raise ValueError(f"Failed to download PDF: {response.status_code}")

    # Set the content type and content disposition headers
    headers = {
        'Content-Type': 'application/pdf',
        'Content-Disposition': f'attachment; filename="{url.split("/")[-1]}"'
    }

    return response.content, headers



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
