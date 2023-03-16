import os
import psycopg2
from flask import Flask, render_template
from dotenv import load_dotenv
import graphene
import requests
import json

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

# filted repo using tags

query = """
  query {
  user(login: "rakshitmehra") {
    repositories(first: 50) {
      nodes {
        owner {
          login
        }
        name
        description
        createdAt
        updatedAt
        issues(
          first: 10
          states: OPEN
          orderBy: {field: UPDATED_AT, direction: DESC}
          labels: ["good first issue","kg foss"]
        ) {
          totalCount
          nodes {
            title
          }
        }
      }
    }
  }
}
"""

headers = {"Authorization": "Bearer API_HERE"}


@app.route("/")
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM books;")
    books = cur.fetchall()
    print(books)
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

# changed

@app.route("/git/repos")
def gitRepos():
  jsonItems = """
  [{
            "createdAt": "2022-07-09T21:23:49Z",
            "description": null,
            "issues": {
              "nodes": [],
              "totalCount": 0
            },
            "name": "Login-Register",
            "owner": {
              "login": "rakshitmehra"
            },
            "updatedAt": "2022-07-09T21:30:29Z"
          },
          {
            "createdAt": "2022-07-17T15:57:34Z",
            "description": null,
            "issues": {
              "nodes": [],
              "totalCount": 0
            },
            "name": "Calculator",
            "owner": {
              "login": "rakshitmehra"
            },
            "updatedAt": "2022-07-17T17:12:52Z"
          },
          {
            "createdAt": "2022-07-19T22:33:57Z",
            "description": "This repository is to allow Hactoberfest 2022 participants to make PR's. This repository aims to help beginners \ud83e\udd14 with their first successful Pull Request and Open Source Contribution\ud83d\ude0a\ud83d\ude0a",
            "issues": {
              "nodes": [
                {
                  "title": "longest palindromic substring"
                },
                {
                  "title": "[OpenCV] live sketch program"
                },
                {
                  "title": "Summation of diagonal elements in CPP"
                },
                {
                  "title": "Adding questions for Programming under Binary Trees Topic"
                },
                {
                  "title": "Add any programs related to C++ or Java or Python in following folders"
                },
                {
                  "title": "Put Atleast 30 questions Related to Programming"
                },
                {
                  "title": "Make this Website Dynamic, So that We can put the questions directly, so that not changing the code again nd again."
                },
                {
                  "title": "Adding animation"
                },
                {
                  "title": "Adding Top Interview Questions"
                },
                {
                  "title": "A try to laugh challenge webpage "
                }
              ],
              "totalCount": 10
            },
            "name": "Quiz-application",
            "owner": {
              "login": "rakshitmehra"
            },
            "updatedAt": "2023-01-03T15:17:12Z"
          }]
  """
  repo = json.loads(jsonItems)
  return render_template("Repos.html",repos=repo)


if __name__ == "__main__":
    app.run(debug=True)

