import os
import psycopg2
from flask import Flask, render_template
from dotenv import load_dotenv
import graphene
import requests

load_dotenv()


app = Flask(__name__)


def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ["DB_URL"],
        database=os.environ["DB_DB"],
        user=os.environ["DB_USERNAME"],
        password=os.environ["DB_PASSWORD"],
    )
    return conn


query = """
{
  viewer {
    login
  }
}
"""

query = """
{
  viewer {
    pullRequests(first: 100, orderBy: {field: UPDATED_AT, direction: DESC}) {
      nodes {
        repository {
          name
          isPrivate
        }
      }
    }
  }
}


"""

headers = {"Authorization": "Bearer xxx"}


@app.route("/")
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM books;")
    books = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("index.html", books=books)


@app.route("/git")
def gitget():
    request = requests.post(
        "https://api.github.com/graphql", json={"query": query}, headers=headers
    )
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception(
            "Query failed to run by returning code of {}. {}".format(
                request.status_code, query
            )
        )


if __name__ == "__main__":
    app.run(debug=True)

