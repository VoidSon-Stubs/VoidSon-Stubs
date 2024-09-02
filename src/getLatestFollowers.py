import requests
import json
import sys
import re

def get_latest_followers(handle, token, readme_path):
    headers = {
        "Authorization": f"token {token}"
    }

    followers = []
    cursor = None

    while True:
        query = f'''
        query {{
            user(login: "{handle}") {{
                followers(first: 12{f', after: "{cursor}"' if cursor else ''}) {{
                    pageInfo {{
                        endCursor
                        hasNextPage
                    }}
                    nodes {{
                        login
                        name
                        databaseId
                    }}
                }}
            }}
        }}
        '''
        response = requests.post("https://api.github.com/graphql", json={"query": query}, headers=headers)
        if not response.ok or "data" not in response.json():
            print("Failed to fetch data from GitHub API")
            exit(1)
        
        res = response.json()["data"]["user"]["followers"]
        followers.extend(res["nodes"])
        if not res["pageInfo"]["hasNextPage"] or len(followers) >= 12:
            break
        cursor = res["pageInfo"]["endCursor"]

    followers = followers[:12]  # Get the latest 12 followers

    html = "<table>\n"
    for i, follower in enumerate(followers):
        login = follower["login"]
        name = follower["name"] if follower["name"] else login
        id = follower["databaseId"]
        if i % 4 == 0:
            if i != 0:
                html += "  </tr>\n"
            html += "  <tr>\n"
        html += f'''    <td align="center">
      <a href="https://github.com/{login}">
        <img src="https://avatars.githubusercontent.com/u/{id}" width="100px;" alt="{login}"/>
      </a>
      <br />
      <a href="https://github.com/{login}">{name}</a>
    </td>
'''

    html += "  </tr>\n</table>"

    with open(readme_path, "r") as readme:
        content = readme.read()

    new_content = re.sub(r"(?<=<!--START_SECTION:latest-followers-->)[\s\S]*(?=<!--END_SECTION:latest-followers-->)", f"\n{html}\n", content)

    with open(readme_path, "w") as readme:
        readme.write(new_content)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python getLatestFollowers.py <GitHub_Username> <GitHub_Token> <README_File_Path>")
        exit(1)

    github_username = sys.argv[1]
    github_token = sys.argv[2]
    readme_file_path = sys.argv[3]

    get_latest_followers(github_username, github_token, readme_file_path)
