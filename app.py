import os
import psycopg2
from dotenv import load_dotenv
import graphene
import requests
from flask import Flask,render_template,url_for,request,redirect, make_response
from flask_dance.contrib.github import make_github_blueprint, github
from flask_login import logout_user
import json

load_dotenv()


app = Flask(__name__)
app.config["SECRET_KEY"]="abcde"
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
github_blueprint = make_github_blueprint(client_id=os.environ['GITHUB_CLIENT_ID'],
                                         client_secret=os.environ['GITHUB_CLIENT_SECRET'])

app.register_blueprint(github_blueprint, url_prefix='/github_login')


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

query_to_issues = """
  {
  search(first: 100, type: ISSUE, query: "label:kg-foss state:closed") {
    issueCount
    pageInfo {
      hasNextPage
      endCursor
    }
    edges {
      node {
        ... on Issue {
          id
          createdAt
          title
          url
          repository {
            name
          }
          assignees(first: 10) {
          nodes {
            login
          }
        }
        }
      }
    }
  }
}
"""

headers = {"Authorization": "Bearer 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"}


@app.route("/")
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM books;")
    books = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("index.html", books=books)
@app.route('/login')
def github_login():

    if not github.authorized:
        return redirect(url_for('github.login'))
    else:
        account_info = github.get('/user')
        if account_info.ok:
            account_info_json = account_info.json()
            print(account_info_json)
            return '<h1>Your Github name is {}'.format(account_info_json['login'])

    return '<h1>Request failed!</h1>'

@app.route("/logout")
def github_logout():
    del github_blueprint.token
    # print(github_blueprint.token)
    return 'logged out'

@app.route("/git")
def gitget():
    request = requests.post(
        "https://api.github.com/graphql", json={"query": query_to_issues}, headers=headers
    )
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception(
            "Query failed to run by returning code of {}. {}".format(
                request.status_code, query
            )
        )


@app.route("/issues", methods=["POST","GET"])
def add_issues():
    if not github.authorized:
        return redirect(url_for('github.login'))
    if request.method == "POST":
        conn = get_db_connection()
        cur = conn.cursor()
        sql = """INSERT INTO UserIssues(issue_id,user_id,repo_id,status,created_at, updated_at) VALUES(%s,%s,%s,%s,%s,%s)"""
        values = (request.form["issue_id"],request.form["user_id"],request.form["repo_id"],request.form["status"],request.form["created_at"],request.form["updated_at"])
        cur.execute(sql,values)
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("index"))
    gql_query="""query {
  viewer{
    repositories(isFork:true,first:10) {
      totalCount
      edges {
        node {
          id
          name
          url
          parent {
            id
            nameWithOwner
            issues(first:20,) {
            edges {
              node {
                id
                body
                bodyUrl
                assignees(first:10) {
                  edges {
                    node {
                      id
                      login
                      isViewer
                      name
                    }
                  }
                }
              }
            }
          }
        }   
        }
      }
    }
  }
}

    """
    headers = {"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"}

    response = requests.post("https://api.github.com/graphql", json= {"query":gql_query}, headers=headers)
    if response.status_code == 200:
        # return render_template("issues.html",issues=response.content)
        return render_template("issues.html",issues=response.json()['data']['viewer']['repositories']['edges'])
    return redirect(url_for("index"))

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

