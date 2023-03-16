https://www.digitalocean.com/community/tutorials/how-to-use-a-postgresql-database-in-a-flask-application
<https://gist.github.com/gbaman/b3137e18c739e0cf98539bf4ec4366ad>


# Local Setup Steps

## Prerequisites
- [Python 3.7+](https://www.python.org/downloads/release/python-370/)
- [GIT CLI](https://git-scm.com/downloads)
- [vscode](https://code.visualstudio.com/download)
- [supabase account](https://supabase.com/)


### Fork the Repository

Towards the top right, click on the `fork` button and create a fork.

### Clone your Forked Repository

Click on the `code` button and copy the URL that is displayed under the `HTTPS` tab.

After copying the link, open a CMD/Terminal and enter the following command

```
git clone YOUR_COPIED_URL
cd kgfoss
```
### Create a virtual environment for the project
```
pip install virtualenv 
virtualenv env
```
### Activate your environment
```
env\Scripts\activate
```
[Refer to this article if any issues](https://www.geeksforgeeks.org/creating-python-virtual-environment-windows-linux/)

Install dependencies
```
pip install -r requirements.txt
```
## Setting up supabase
### Create a new project
- Login to [supabase](https://supabase.com/) and click on the `new project` button on your dashboard.
- Create an organisation with any name select `personal` as the type.
- After creating an organisation, Enter a name and password for your Database and click the `Create new project`
(Keep the password somewhere safe as you will not be able to view it again)
- On your left hand side, click on the `databases` button and click on `new table`
- Name it `UserIssues` and add the following fields
```
    issue id :varchar
    user_id :varchar
    repo_id : varchar
    status : varchar
    created_at : timestampz (in utc)
    updated_at : timestampz (in utc)
```
- Create another table named `Users` with the following fields
```

    roll_no : varchar
    college : varchar
    year : int2
    dept : varchar
    mobile : int2
    email : int2

```
### DB Credentials

In your dashboard go to `Project Settings` > `Database`. From here you can get your credentials which you can add to your .env file

DB_USERNAME=User
DB_PASSWORD=Password
DB_URL=Host
DB_DB=database name


## Personal Access Token
- Click on your avatar on the top right corner and open your settings page.

- From there, scroll down and click on `Developer Settings`

- Select `Personal Access Tokens` > `Fine-Grained Tokens` > `Generate New Token`

- Enter a name for it and click `Generate Token`

- Copy this token and add the following line to your `.env` file

```
GITHUB_TOKEN=your_personal_access_token
```

Your final `.env` file should look like this

```
DB_USERNAME=User
DB_PASSWORD=Password
DB_URL=Host
DB_DB=database name
GITHUB_TOKEN=personal_access_token  
```


## Run the app

```
python app.py

``` 

## Adding an OAuth app

- click your avatar on the top right and go to `Settings`
- Scroll down and click on `Developer Settings`
- Click on `OAuth Apps` > `New OAuth App`
- Enter any name for the name
- For URL enter `http://127.0.0.1:5000`
- For Callback URL enter `http://127.0.0.1:5000/github_login/github/authorized`
- Click on `register` to finish creation of your OAuth app
- Get your Client ID and Generate your Client Secret and add it to your .env file as
```
GITHUB_CLIENT_SECRET=client_secret
GITHUB_CLIENT_ID=client_ID
```

