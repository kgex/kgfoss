import os
import psycopg2
from dotenv import load_dotenv
import graphene
import requests
from flask import Flask,render_template,url_for,request,redirect, make_response, json
from flask_dance.contrib.github import make_github_blueprint, github
from flask_login import logout_user
from datetime import datetime, timedelta

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
GITHUB_AUTH_TOKEN = os.environ["GITHUB_AUTH_TOKEN"]

headers = {"Authorization": "Bearer " + GITHUB_AUTH_TOKEN }


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


@app.route('/leaderboard2')
def lederboard2():
    query_to_leaderboard = """
    {
  repository(owner: "kgex", name: "kgfoss") {
    pullRequests(last: 10, states: [MERGED]) {
      nodes {
        title
        mergedAt
        author{
          login
        }
        mergedBy {
          login
        }
        mergeCommit {
          oid
          message
        }
      }
    }
  }
}
      """
    request = requests.post(
        "https://api.github.com/graphql", json={"query": query_to_leaderboard}, headers=headers
    )

    data = json.dumps( [1.0,2.0,3.0] )

    if request.status_code == 200:
        return render_template("leaderboard.html",data=request.json()['data']['repository']['pullRequests']['nodes'])
    else:
        raise Exception(
            "Query failed to run by returning code of {}. {}".format(
                request.status_code, query
            )
        )

# usersz = ["Brijesh-m-14", "Ashwin-d-27", "GnanaChandruKR", "Thanush2412", "ELAKIYA-SEKAR", "vasanthakumar2004", "AkshayaVarshieni14", "JasferI", "vikrantvikaasa27"]

usersz = ["nivu", "spikeysanju", "Brijesh-m-14"]
queries = []

for i, use in enumerate(usersz):
    print(use)
    query = f'''
    user{i}: user(login: "{use}") {{
      name
      pullRequests(last: 10, states: MERGED, orderBy: {{field: UPDATED_AT, direction: DESC}}) {{
        nodes {{
          title
          url
          state
          updatedAt
          repository {{
            nameWithOwner
          }}
        }}
      }}
    }}
    '''
    queries.append(query)
print(len(queries))
print(queries)

graphql_query = "query {" + "\n".join(queries) + "}"
    
print(graphql_query)

@app.route('/leaderboard')
def lederboard():
    request = requests.post(
        "https://api.github.com/graphql", json={"query": graphql_query}, headers=headers
    )

    if request.status_code == 200:
        resp = request.json()['data']
        data = []
        for key in resp.keys():
            if resp[key] != None:
              name = resp[key]['name']
              nodes = len(resp[key]['pullRequests']['nodes'])
              prs = []
              for pr in resp[key]['pullRequests']['nodes']:
                  prs.append(pr['title'])
              data.append({"name": name, "nodes": nodes, "prs": prs})
        return render_template("realboard.html",data=data)
    else:
        raise Exception(
            "Query failed to run by returning code of {}. {}".format(
                request.status_code, query
            )
        )
    
CONTRIBUTORS = ["nivu", "PranikaBaby", "nivu", "nivu"]


QUERY = """
query ($userLogins:[String!]!, $since:DateTime!, $after:String) {
  search(query: "is:pr is:merged author:{userLogins} merged:>{since} state:closed", type: ISSUE, first: 100, after: $after) {
    edges {
      cursor
      node {
        ... on PullRequest {
          author {
            login
          }
          repository {
            nameWithOwner
          }
          mergedAt
        }
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
"""


def run_query(query, variables):
    # headers = {"Authorization": f"Bearer {API_TOKEN}"}
    response = requests.post("https://api.github.com/graphql", json={"query": query, "variables": variables}, headers=headers)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise Exception(f"Query failed to run: {response.text}")

@app.route("/leader")
def leader():
    # Calculate the start date for the query
    since = datetime.now() - timedelta(days=2)
    
    # Retrieve pull requests from the GitHub GraphQL API for each contributor
    pr_counts = {contributor: 0 for contributor in CONTRIBUTORS}
    for contributor in CONTRIBUTORS:
        end_cursor = None
        while True:
            query = QUERY % (",".join([f'"{contributor}"']), since.strftime("%Y-%m-%dT%H:%M:%SZ"), end_cursor)
            result = run_query(query, {})
            pulls = result["data"]["search"]["edges"]
            
            # Count the number of successful pull request merges by the contributor
            for pull in pulls:
                if pull["node"]["author"] and pull["node"]["author"]["login"] == contributor and pull["node"]["mergedAt"] is not None:
                    pr_counts[contributor] += 1
            
            # Check if there are more results to retrieve
            if result["data"]["search"]["pageInfo"]["hasNextPage"]:
                end_cursor = result["data"]["search"]["pageInfo"]["endCursor"]
            else:
                break
    
    # Sort contributors by number of successful pull request merges
    sorted_contributors = sorted(pr_counts, key=pr_counts.get, reverse=True)
    
    # Create a list of (username, successful_pr_merge_count) tuples for the top 4 contributors
    leaderboard = [(contributor, pr_counts[contributor]) for contributor in sorted_contributors[:4]]
    
    # Render the leaderboard template with the leaderboard data
    return render_template("leader.html", leaderboard=leaderboard)


if __name__ == "__main__":
    app.run(debug=True)

