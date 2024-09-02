import requests
import json
import sys
import re

if __name__ == "__main__":
    assert len(sys.argv) == 4
    handle = sys.argv[1]
    token = sys.argv[2]
    readmePath = sys.argv[3]

    headers = {
        "Authorization": f"token {token}"
    }

    query = '''
    query {
        user(login: "%s") {
            followers(last: 12) {
                nodes {
                    login
                    avatarUrl
                }
            }
        }
    }
    ''' % handle

    response = requests.post(
        "https://api.github.com/graphql",
        json.dumps({"query": query}),
        headers=headers
    )

    if not response.ok or "data" not in response.json():
        print("Failed to fetch data from GitHub API")
        sys.exit(1)

    followers_data = response.json()["data"]["user"]["followers"]["nodes"]

    html = "<table>\n<tr>\n"
    for follower in followers_data:
        html += f'''
        <td align="center">
            <a href="https://github.com/{follower['login']}">
                <img src="{follower['avatarUrl']}" width="100px;" alt="{follower['login']}"/>
            </a>
            <br />
            <a href="https://github.com/{follower['login']}">{follower['login']}</a>
        </td>
        '''
    html += "\n</tr>\n</table>"

    with open(readmePath, "r") as readme_file:
        content = readme_file.read()

    new_content = re.sub(
        r"(?<=<!--START_SECTION:latest-followers-->)[\s\S]*(?=<!--END_SECTION:latest-followers-->)",
        f"\n{html}\n",
        content
    )

    with open(readmePath, "w") as readme_file:
        readme_file.write(new_content)
