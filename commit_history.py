import os
import subprocess
import shutil
import MergeMiner
import logging

# Set path
path_prefix = '/home/ppp/Research_Projects/Merge_Conflicts'
workspace = 'Resource/workspace'
logger_path = 'Script/github_star_projects/script.log'
output_path = 'Script/github_star_projects/commit_hisotry.txt'
# create logger with 'script_logger'
logger = logging.getLogger('script_logger')
logger.setLevel(logging.INFO)
# create file handler which logs even debug messages
fh = logging.FileHandler(os.path.join(path_prefix, logger_path))
# fh = logging.FileHandler("script.log")
fh.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
# Set URL
# URL = 'https://github.com/spring-projects/spring-boot'
# URL = 'https://github.com/spring-projects/spring-framework'
# URL = 'https://github.com/alibaba/spring-cloud-alibaba'
# URL = 'https://github.com/alibaba/nacos'
URL = 'https://github.com/elastic/elasticsearch'
try:
    os.chdir(os.path.join(path_prefix, workspace))
    project_name = MergeMiner.extract_file_name(URL, 4)
    MergeMiner.git_clone(URL, project_name, logger)
    os.chdir(os.path.join(path_prefix, workspace, project_name))
    MergeMiner.git_log(os.path.join(path_prefix, workspace, 'log_file'), logger)
    commits_info = MergeMiner.filter_merge_commits(logger)
    with open(os.path.join(path_prefix, output_path), 'w') as f:
        f.write('Project:\t' + project_name + '\n')
        f.write('Total number of commits is ' + str(commits_info['Num_commits']) + '\n')
        f.write('Total number of merge commits is ' + str(commits_info['Num_merge_commits']) + '\n')
        f.write('\n')
        for commit in commits_info['merge_commits']:
            f.write('Base:\t' + commit['Base']+'\n')
            f.write('Left:\t' + commit['Left'] + '\n')
            f.write('Right:\t' + commit['Right'] + '\n')
            f.write('Child:\t' + commit['Child'] + '\n')
            f.write('\n')
except Exception as e:
    print(str(e))
finally:
    pass
