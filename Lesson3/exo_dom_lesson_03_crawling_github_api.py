import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
from github import Github
from multiprocessing import Pool
import pandas as pd
import numpy as np
import json

repos = {"user": [], "repo": [], "stars_count": []}
g = Github(login_or_token="117cec771fd596f7152d6117a7f4ec17e6e5ef96")


def get_active_github_users():
    active_users = []
    soup = get_soup_for_url("https://gist.github.com/paulmillr/2657075")
    for child in soup.find_all("table")[0].find_all("tbody")[0].find_all("tr"):
        active_users.append(str(child.contents[3].contents[0].string))
    return active_users


def get_soup_for_url(url):
    res = requests.get(url)
    if res.status_code == 200:
        return BeautifulSoup(res.text, 'html.parser')


def error_handler(error):
    print("error")
    print(error)


def get_stars_dict(users):
    p = Pool(
        4)  # Limit the number of process in order not to exceed the rate limit
    for user in users:
        p.apply_async(get_stars_for_user, (user,),
                      callback=add_user_repos,
                      error_callback=error_handler)
    p.close()
    p.join()


def get_stars_for_user(user):
    """Get the stars of a user using the PyGitHub python API"""
    print("getting stars for user " + user)
    repos = g.get_user(user).get_repos()
    extracted_repos = [[user, repo.name, repo.stargazers_count] for repo in
                       repos]
    return extracted_repos


def get_stars_for_user_using_api(user):
    """
    Get the stars of a user using the GitHub API

    For now, this way of using the API doesn't handle multiple pages
    """
    print("getting stars for user " + user)
    http_repos = requests.get(
        "https://api.github.com/users/" + user + "/repos",
        auth=HTTPBasicAuth("cyrnguyen",
                           "117cec771fd596f7152d6117a7f4ec17e6e5ef96"))
    repos = json.loads(http_repos.text)
    return [[user, repo["name"], repo["stargazers_count"]] for repo in repos]


def add_user_repos(user_repos):
    for user_repo in user_repos:
        repos["user"].append(user_repo[0])
        repos["repo"].append(user_repo[1])
        repos["stars_count"].append(user_repo[2])


def get_dataframe_from_table(repo_dict):
    return pd.DataFrame(repo_dict, index=np.arange(len(repo_dict["user"])))


if __name__ == '__main__':
    active_users = get_active_github_users()
    get_stars_dict(active_users)
    repos = get_dataframe_from_table(repos)
    print(repos.head())
    star_count_mean = repos.drop(["repo"], axis=1).groupby("user").mean() \
        .sort_values(by="stars_count", axis=0, ascending=False)
    print(star_count_mean)
