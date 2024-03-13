import os
import requests
import json
path = '/home/ppp/Research_Projects/Merge_Conflicts/Script/github_star_projects/repository_snapshot'
Top_1K = 'https://api.github.com/search/repositories?q=stars%3A%3E2000+language:java&sort=stars&per_page=100'
Page = '&page='
Iter_limit = 10
commit_prefix = 'https://api.github.com/repos/'
user = 'XXX'
pwd = 'XXX'
# repository_list = []
# for i in range(Iter_limit):
#     r = requests.get(Top_1K + Page + str(i+1), auth=(user, pwd))
#     repository_list = repository_list + r.json()['items']
# with open(os.path.join(path, 'respositories.json'), 'w') as fp:
#     json.dump(repository_list, fp)
with open(os.path.join(path, 'respositories.json'), 'r') as fp:
    result = json.load(fp)
temp = list({'url': k['html_url'], 'name': k['full_name']} for k in result)
requests_temp = list(requests.get(commit_prefix + item['name'] + '/commits', auth=(user, pwd)) for item in temp)
# if all(requests_temp.status == 200):
commit_list = list(k.json()[0]['sha'] for k in requests_temp if k.status_code == 200)
final_list = list({'URL': temp[i]['url'], 'name': temp[i]['name'], 'latest_commit': commit_list[i]}
                  for i in range(len(commit_list)))
# write into file
with open(os.path.join(path, 'Top_1K.json'), 'w') as fp:
    json.dump(final_list, fp)
