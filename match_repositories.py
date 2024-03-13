import os
import json
import requests
path = '/home/ppp/Research_Projects/Merge_Conflicts/Script/github_star_projects/repository_snapshot/'
github_repositories = 'respositories.json'
old_list = 'Paper_list'
new_list = 'Ranked_list'
api_prefix = 'https://api.github.com/repos/'
user = 'bowenshen'
pwd = 'f9da6ca6532d67243fa8ed7b85ec8fd25302f45d'
with open(os.path.join(path, github_repositories), 'r') as fp:
    github_repositories = json.load(fp)
with open(os.path.join(path, old_list), 'r') as fp:
    URL_list = [line.rstrip('\n') for line in fp]
# star_list = []
# for i in range(len(URL_list)):
#     url = URL_list[i]
#     name = url.split('/', 3)[-1]
#     request = requests.get(api_prefix + name, auth=(user, pwd))
#     if request.status_code == 200:
#         star_list.append({'URL': url, 'stars': request.json()['stargazers_count']})
# # star_list = list({'URL': url,
# #                   'stars': requests.get(commit_prefix + url.split('/', 3)[-1] + '/commits', auth=(user, pwd)).
# #                  json()[0]['sha']} for url in URL_list)
# # star_list = list({'URL': url, 'stars': item['stargazers_count']} for url in URL_list for item in github_repositories
# #                     if item['full_name'] in url)
# ranked_list = sorted(star_list, key=lambda item: item['stars'])
# with open(os.path.join(path, new_list), 'w') as fp:
#     json.dump(ranked_list, fp)
with open(os.path.join(path, new_list), 'r') as fp:
    ranked_list = json.load(fp)
for i in range(len(ranked_list)):
    for j in range(1000):
        if ranked_list[i]['URL'] == github_repositories[j]['html_url']:
            print("Project " + ranked_list[i]['URL'] + "\tin rank " + str(j) + "\thave starts: " + str(github_repositories[j]['stargazers_count']) + '\n')
if True:
    pass
else:
    pass