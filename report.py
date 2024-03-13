# Script to pre-select projects in github
import json
import os
import logging
import requests
import shutil
import subprocess
# import another user module
import MergeMiner
from ValueEnum import ValueEnum
# import global variable: mode
from script import mode


class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if obj in ValueEnum:
            return {"__enum__": str(obj)}
        return json.JSONEncoder.default(self, obj)


def as_enum(data):
    if "__enum__" in data:
        name, member = data["__enum__"].split(".")
        return getattr(ValueEnum, member)
    else:
        return data


# Set path
if mode == "server":
    path_prefix = '/home/bowen/Research_Projects/Merge_Conflicts'
elif mode == "local":
    path_prefix = '/home/ppp/Research_Projects/Merge_Conflicts'
else:
    raise MergeMiner.AbnormalBehaviourError("Wrong mode")
# project_list_path = 'Script/github_star_projects/URL_list'
# project_list_path = 'Script/github_star_projects/valid_list'
project_list_path = 'Script/github_star_projects/debug_list'
# project_list_path = 'Script/github_star_projects/switch_order'
projects_record_path = 'Script/github_star_projects/projects_record.json'
projects_record_folder_path = 'Script/github_star_projects/projects_record'
workspace = 'Resource/workspace'
original_copy_path = 'Resource/Original_copy_projects'
logger_path = 'Script/github_star_projects/script.log'
report_path = 'Script/github_star_projects/report'
# commit_path = 'Resource/Commits_info'
# Global variable (access with module)
projects_record = []


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


# All data are stored in projects_record json file
def save_data():
    with open(os.path.join(path_prefix, projects_record_path), 'w') as outfile:
        json.dump(projects_record, outfile, cls=EnumEncoder)


def save_splitted_data(URL):
    project_name = URL.split('/')[-1]
    if not os.path.exists(os.path.join(path_prefix, projects_record_folder_path)):
        os.mkdir(os.path.join(path_prefix, projects_record_folder_path))
    with open(os.path.join(path_prefix, projects_record_folder_path, project_name), 'w') as outfile:
        json.dump(projects_record[URL], outfile, cls=EnumEncoder)


def read_data():
    if os.path.exists(os.path.join(path_prefix, projects_record_path)):
        with open(os.path.join(path_prefix, projects_record_path), 'r') as infile:
            # nonlocal projects_record
            return json.load(infile, object_hook=as_enum)
    else:
        return {}


def view_data(path):
    if os.path.exists(path):
        with open(path, 'r') as infile:
            # nonlocal projects_record
            return json.load(infile, object_hook=as_enum)
    else:
        return {}


# view splited generated project record
def report_data():
    records = [f for f in os.listdir(os.path.join(path_prefix, projects_record_folder_path))
               if os.path.isfile(os.path.join(path_prefix, projects_record_folder_path, f))]
    with open(os.path.join(path_prefix, report_path), 'w') as f:
        for item in records:
            # json_info = []
            json_info = view_data(os.path.join(path_prefix, projects_record_folder_path, item))
            f.write("Project " + item + " summary\n")
            # Type
            f.write("Type of project: " + json_info['Type'] + "\n")
            # Total commits
            num = json_info['Num_commits']
            f.write("Number of commits: " + str(num) + "\n")
            # Total merge commits
            num = json_info['Num_merge_commits']
            f.write("Number of merge commits: " + str(num) + "\n")
            # Total commits pass git merge
            num = len(
                list(k for k, v in json_info['Resolved_Commits'].items() if v['Git_mergeable'] == ValueEnum.true))
            f.write("Number of commits are git mergeable: " + str(num) + "\n")
            # Total commits fail git merge
            num = len(
                list(k for k, v in json_info['Resolved_Commits'].items() if v['Git_mergeable'] == ValueEnum.false))
            f.write("Number of commits are not git mergeable: " + str(num) + "\n")
            # Total commits unknown git merge
            num = len(
                list(k for k, v in json_info['Resolved_Commits'].items() if v['Git_mergeable'] == ValueEnum.unknown))
            f.write("Number of commits are unknown git mergeable: " + str(num) + "\n")
            # Total commits are applicable for automatic compilation
            num = len(list(k for k, v in json_info['Resolved_Commits'].items() if v['Automatic_compilation_applicable']
                           == ValueEnum.true))
            f.write("Number of commits are applicable for automatic compilation:" + str(num) + "\n")
            # Total commits are not applicable for automatic compilation
            num = len(list(k for k, v in json_info['Resolved_Commits'].items() if v['Automatic_compilation_applicable']
                           == ValueEnum.false))
            f.write("Number of commits are not applicable for automatic compilation:" + str(num) + "\n")
            # Total commits are unknown applicable for automatic compilation
            num = len(list(k for k, v in json_info['Resolved_Commits'].items() if v['Automatic_compilation_applicable']
                           == ValueEnum.unknown))
            f.write("Number of commits are unknown applicable for automatic compilation:" + str(num) + "\n")
            # Total commits are success for automatic compilation
            num = len(list(k for k, v in json_info['Resolved_Commits'].items() if v['Automatic_compilation_success']
                           == ValueEnum.true))
            f.write("Number of commits are success for automatic compilation:" + str(num) + "\n")
            # Total commits are not success for automatic compilation
            num = len(list(k for k, v in json_info['Resolved_Commits'].items() if v['Automatic_compilation_success']
                           == ValueEnum.false))
            f.write("Number of commits are not success for automatic compilation:" + str(num) + "\n")
            # Total commits are unknown success for automatic compilation
            num = len(list(k for k, v in json_info['Resolved_Commits'].items() if v['Automatic_compilation_success']
                           == ValueEnum.unknown))
            f.write("Number of commits are unknown success for automatic compilation:" + str(num) + "\n")
            # Total commits are true syntactic conflict
            num = len(list(k for k, v in json_info['Resolved_Commits'].items() if v['Syntactic_conflict_status']
                           == ValueEnum.true))
            f.write("Number of commits are syntactic conflicts:" + str(num) + "\n")
            # Total commits are false syntactic conflict
            num = len(list(k for k, v in json_info['Resolved_Commits'].items() if v['Syntactic_conflict_status']
                           == ValueEnum.false))
            f.write("Number of commits are not syntactic conflicts:" + str(num) + "\n")
            # Total commits are unknown syntactic conflict
            num = len(list(k for k, v in json_info['Resolved_Commits'].items() if v['Syntactic_conflict_status']
                           == ValueEnum.unknown))
            f.write("Number of commits are unknown syntactic conflicts:" + str(num) + "\n")
            # Total commits are applicable for automatic test
            num = len(list(k for k, v in json_info['Resolved_Commits'].items() if v['Automatic_test_applicable']
                           == ValueEnum.true))
            f.write("Number of commits are applicable for automatic test:" + str(num) + "\n")
            # Total commits are not applicable for automatic test
            num = len(list(k for k, v in json_info['Resolved_Commits'].items() if v['Automatic_test_applicable']
                           == ValueEnum.false))
            f.write("Number of commits are not applicable for automatic test:" + str(num) + "\n")
            # Total commits are unknown applicable for automatic test
            num = len(list(k for k, v in json_info['Resolved_Commits'].items() if v['Automatic_test_applicable']
                           == ValueEnum.unknown))
            f.write("Number of commits are unknown applicable for automatic test:" + str(num) + "\n")
            # Total commits are success for automatic test
            num = len(list(k for k, v in json_info['Resolved_Commits'].items() if v['Automatic_test_success']
                           == ValueEnum.true))
            f.write("Number of commits are success for automatic test:" + str(num) + "\n")
            # Total commits are not success for automatic test
            num = len(list(k for k, v in json_info['Resolved_Commits'].items() if v['Automatic_test_success']
                           == ValueEnum.false))
            f.write("Number of commits are not success for automatic test:" + str(num) + "\n")
            # Total commits are unknown success for automatic test
            num = len(list(k for k, v in json_info['Resolved_Commits'].items() if v['Automatic_test_success']
                           == ValueEnum.unknown))
            f.write("Number of commits are unknown success for automatic test:" + str(num) + "\n")
            # Total commits are true semantic conflict
            num = len(list(k for k, v in json_info['Resolved_Commits'].items() if v['Semantic_conflict_status']
                           == ValueEnum.true))
            f.write("Number of commits are semantic conflicts:" + str(num) + "\n")
            # Total commits are false semantic conflict
            num = len(list(k for k, v in json_info['Resolved_Commits'].items() if v['Semantic_conflict_status']
                           == ValueEnum.false))
            f.write("Number of commits are not semantic conflicts:" + str(num) + "\n")
            # Total commits are unknown semantic conflict
            num = len(list(k for k, v in json_info['Resolved_Commits'].items() if v['Semantic_conflict_status']
                           == ValueEnum.unknown))
            f.write("Number of commits are unknown semantic conflicts:" + str(num) + "\n")
            f.write("\n")


# report_data()
result1 = view_data('/home/ppp/Research_Projects/Merge_Conflicts/Script/github_star_projects/Experiment/Top100/server/spring-boot')
result2 = view_data('/home/ppp/Research_Projects/Merge_Conflicts/Script/github_star_projects/Experiment/Top100/projects_record/spring-boot')

# commit = {k:v for k,v in result['Resolved_Commits'].items() if v['Semantic_conflict_status'] ==ValueEnum.true}
syn_commit = {k: v for k, v in result['Resolved_Commits'].items() if v['Syntactic_conflict_status'] == ValueEnum.true}
sem_commit = {k: v for k, v in result['Resolved_Commits'].items() if v['Semantic_conflict_status'] == ValueEnum.true}

# Add diff file to the corresponding folders
folder_path = '/home/ppp/Research_Projects/Merge_Conflicts/Script/github_star_projects/server/MergeMiner_output/spring-framework/'
os.chdir('/home/ppp/Research_Projects/Merge_Conflicts/Resource/workspace/spring-framework')
for k in syn_commit.keys():
    MergeMiner.git_diff(syn_commit[k]['Base'], syn_commit[k]['Left'],
                        os.path.join(folder_path, k, "base_left_diff.txt"), logger)
    MergeMiner.git_diff(syn_commit[k]['Base'], syn_commit[k]['Right'],
                        os.path.join(folder_path, k, "base_right_diff.txt"), logger)
    MergeMiner.git_diff(syn_commit[k]['Base'], syn_commit[k]['Child'],
                        os.path.join(folder_path, k, "base_child_diff.txt"), logger)
    MergeMiner.git_diff(syn_commit[k]['Left'], syn_commit[k]['Child'],
                        os.path.join(folder_path, k, "left_child_diff.txt"), logger)
    MergeMiner.git_diff(syn_commit[k]['Right'], syn_commit[k]['Child'],
                        os.path.join(folder_path, k, "right_child_diff.txt"), logger)
if True:
    pass
else:
    pass
