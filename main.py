from dotenv import load_dotenv
import os
import sys
import requests
import json

class PullCloser:
    """
    tool to automate the closure of all pull requests in a github organizaiton
    PullCloser(token: str = gh user token, org: str = gh organization name)
    instance.run() -> closes all prs on all repos in the supplied org
    """

    def __init__(self, token: str, org: str):
        """args: token (gh user token), org (gh organization)"""
        self.__token = token
        self.__org = org
        self.__repos = []
        self.__data = json.dumps({  "state": "closed" })
        self.__headers = {
            "Authorization": f"token {self.__token}",
            "Accept": "application/vnd.github+json"
        }

    def __get_repos(self):
        """builds a list of all repos in the org"""
        get_url = lambda page : f"https://api.github.com/orgs/WDI-SEA/repos?per_page=100&page={page}"

        page = 1
        while True:
            response = requests.get(get_url(page), headers=self.__headers)
            print(f"fetching page {page} of repos")
            response_json = response.json()
            if len(response_json) == 0:
                break

            self.__repos += response_json
            print(f"{len(self.__repos)} retrived so far")
            page += 1

            return self

    def __close_pulls(self):
        """iterate all repos and close all open prs"""

        for repo in self.__repos:
            response = requests.get(f"https://api.github.com/repos/WDI-SEA/{repo['name']}/pulls?per_page=100", headers=self.__headers)
            pulls = response.json()
            for pull in pulls:
                print(f"closing pulls for {pull['url']}")
                pull_response = requests.patch(pull['url'], headers=self.__headers, data=self.__data)

        return self

    def run(self):
        """fetchs all repos in the supplied org, iterates them, and closes all open prs"""
        self.__get_repos().__close_pulls()

        return self

def main():
    load_dotenv()
    GH_TOKEN = os.environ["GH_TOKEN"]
    if len(sys.argv) < 2:
        print("script requires a valid github organization as an argument")
        return
    ORG = sys.argv[1]

    pr_bot = PullCloser(GH_TOKEN, ORG)
    pr_bot.run()

if __name__ == "__main__":
    main()
