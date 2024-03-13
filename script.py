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
from EnumEncoder import EnumEncoder, as_enum

# global mode to select server/local
global mode
# mode = 'server'
mode = 'local'
resume_project = True

# class EnumEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if obj in ValueEnum:
#             return {'__enum__': str(obj)}
#         return json.JSONEncoder.default(self, obj)
#
#
# def as_enum(data):
#     if '__enum__' in data:
#         name, member = data['__enum__'].split('.')
#         return getattr(ValueEnum, member)
#     else:
#         return data


# Set path
if mode == 'server':
    path_prefix = '/home/bowen/Research_Projects/Merge_Conflicts'
elif mode == 'local':
    path_prefix = '/home/ppp/Research_Projects/Merge_Conflicts'
else:
    raise MergeMiner.AbnormalBehaviourError('Wrong mode')


# project_list_path = 'Script/github_star_projects/URL_list'
project_list_path = 'Script/github_star_projects/valid_list'
# project_list_path = 'Script/github_star_projects/debug_list'
# project_list_path = 'Script/github_star_projects/switch_order'
# project_record_path = 'Script/github_star_projects/project_record.json'
project_record_folder_path = 'Script/github_star_projects/projects_record'
workspace = 'Resource/workspace'
original_copy_path = 'Resource/Original_copy_projects'
logger_path = 'Script/github_star_projects/logger'
report_path = 'Script/github_star_projects/report'
# commit_path = 'Resource/Commits_info'
# Global variable (access with module)
project_record = []

# create logger to record complete info
# create logger with 'script_logger'
logger = logging.getLogger('script_logger')
logger.setLevel(logging.INFO)
# create file handler which logs even debug messages
fh = logging.FileHandler(os.path.join(path_prefix, logger_path, 'script.log'))
# fh = logging.FileHandler('script.log')
fh.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)


# All data are stored in project_record json file in project_record_folder_path
def save_data(URL):
    project_name = URL.split('/')[-1]
    if not os.path.exists(os.path.join(path_prefix, project_record_folder_path)):
        os.mkdir(os.path.join(path_prefix, project_record_folder_path))
    with open(os.path.join(path_prefix, project_record_folder_path, project_name), 'w') as outfile:
        json.dump(project_record, outfile, cls=EnumEncoder)


def read_data(URL):
    project_name = URL.split('/')[-1]
    if os.path.exists(os.path.join(path_prefix, project_record_folder_path, project_name)):
        with open(os.path.join(path_prefix, project_record_folder_path, project_name), 'r') as infile:
            # nonlocal project_record
            return json.load(infile, object_hook=as_enum)
    else:
        return {}


def view_data(path):
    if os.path.exists(path):
        with open(path, 'r') as infile:
            # nonlocal project_record
            return json.load(infile, object_hook=as_enum)
    else:
        return {}


# view generated project record
def report_data():
    records = [f for f in os.listdir(os.path.join(path_prefix, project_record_folder_path))
               if os.path.isfile(os.path.join(path_prefix, project_record_folder_path, f))]
    with open(os.path.join(path_prefix, report_path), 'w') as f:
        for item in records:
            # json_info = []
            json_info = view_data(os.path.join(path_prefix, project_record_folder_path, item))
            f.write('Project ' + item + ' summary\n')
            # Type
            f.write('Type of project: ' + json_info['Type'] + '\n')
            # Total commits
            num = json_info['Num_commits']
            f.write('Number of commits: ' + str(num) + '\n')
            # Total merge commits
            num = json_info['Num_merge_commits']
            f.write('Number of merge commits: ' + str(num) + '\n')
            # Total commits pass git merge
            num = len(
                list(k for k, v in json_info['Resolved_Commits'].items() if v['Git_mergeable'] == ValueEnum.true))
            f.write('Number of commits are git mergeable: ' + str(num) + '\n')
            # Total commits fail git merge
            num = len(
                list(k for k, v in json_info['Resolved_Commits'].items() if v['Git_mergeable'] == ValueEnum.false))
            f.write('Number of commits are not git mergeable: ' + str(num) + '\n')
            # Total commits unknown git merge
            num = len(
                list(k for k, v in json_info['Resolved_Commits'].items() if v['Git_mergeable'] == ValueEnum.unknown))
            f.write('Number of commits are unknown git mergeable: ' + str(num) + '\n')
            # Total commits are applicable for automatic compilation
            num = len(list(k for k, v in json_info['Resolved_Commits'].items() if v['Automatic_compilation_applicable']
                           == ValueEnum.true))
            f.write('Number of commits are applicable for automatic compilation:' + str(num) + '\n')
            # Total commits are not applicable for automatic compilation
            num = len(list(k for k, v in json_info['Resolved_Commits'].items() if v['Automatic_compilation_applicable']
                           == ValueEnum.false))
            f.write('Number of commits are not applicable for automatic compilation:' + str(num) + '\n')
            # Total commits are unknown applicable for automatic compilation
            num = len(list(k for k, v in json_info['Resolved_Commits'].items() if v['Automatic_compilation_applicable']
                           == ValueEnum.unknown))
            f.write('Number of commits are unknown applicable for automatic compilation:' + str(num) + '\n')
            # Total commits are success for automatic compilation
            num = len(list(k for k, v in json_info['Resolved_Commits'].items() if v['Automatic_compilation_success']
                           == ValueEnum.true))
            f.write('Number of commits are success for automatic compilation:' + str(num) + '\n')
            # Total commits are not success for automatic compilation
            num = len(list(k for k, v in json_info['Resolved_Commits'].items() if v['Automatic_compilation_success']
                           == ValueEnum.false))
            f.write('Number of commits are not success for automatic compilation:' + str(num) + '\n')
            # Total commits are unknown success for automatic compilation
            num = len(list(k for k, v in json_info['Resolved_Commits'].items() if v['Automatic_compilation_success']
                           == ValueEnum.unknown))
            f.write('Number of commits are unknown success for automatic compilation:' + str(num) + '\n')
            # Total commits are true syntactic conflict
            num = len(list(k for k, v in json_info['Resolved_Commits'].items() if v['Syntactic_conflict_status']
                           == ValueEnum.true))
            f.write('Number of commits are syntactic conflicts:' + str(num) + '\n')
            # Total commits are false syntactic conflict
            num = len(list(k for k, v in json_info['Resolved_Commits'].items() if v['Syntactic_conflict_status']
                           == ValueEnum.false))
            f.write('Number of commits are not syntactic conflicts:' + str(num) + '\n')
            # Total commits are unknown syntactic conflict
            num = len(list(k for k, v in json_info['Resolved_Commits'].items() if v['Syntactic_conflict_status']
                           == ValueEnum.unknown))
            f.write('Number of commits are unknown syntactic conflicts:' + str(num) + '\n')
            # Total commits are applicable for automatic test
            num = len(list(k for k, v in json_info['Resolved_Commits'].items() if v['Automatic_test_applicable']
                           == ValueEnum.true))
            f.write('Number of commits are applicable for automatic test:' + str(num) + '\n')
            # Total commits are not applicable for automatic test
            num = len(list(k for k, v in json_info['Resolved_Commits'].items() if v['Automatic_test_applicable']
                           == ValueEnum.false))
            f.write('Number of commits are not applicable for automatic test:' + str(num) + '\n')
            # Total commits are unknown applicable for automatic test
            num = len(list(k for k, v in json_info['Resolved_Commits'].items() if v['Automatic_test_applicable']
                           == ValueEnum.unknown))
            f.write('Number of commits are unknown applicable for automatic test:' + str(num) + '\n')
            # Total commits are success for automatic test
            num = len(list(k for k, v in json_info['Resolved_Commits'].items() if v['Automatic_test_success']
                           == ValueEnum.true))
            f.write('Number of commits are success for automatic test:' + str(num) + '\n')
            # Total commits are not success for automatic test
            num = len(list(k for k, v in json_info['Resolved_Commits'].items() if v['Automatic_test_success']
                           == ValueEnum.false))
            f.write('Number of commits are not success for automatic test:' + str(num) + '\n')
            # Total commits are unknown success for automatic test
            num = len(list(k for k, v in json_info['Resolved_Commits'].items() if v['Automatic_test_success']
                           == ValueEnum.unknown))
            f.write('Number of commits are unknown success for automatic test:' + str(num) + '\n')
            # Total commits are true semantic conflict
            num = len(list(k for k, v in json_info['Resolved_Commits'].items() if v['Semantic_conflict_status']
                           == ValueEnum.true))
            f.write('Number of commits are semantic conflicts:' + str(num) + '\n')
            # Total commits are false semantic conflict
            num = len(list(k for k, v in json_info['Resolved_Commits'].items() if v['Semantic_conflict_status']
                           == ValueEnum.false))
            f.write('Number of commits are not semantic conflicts:' + str(num) + '\n')
            # Total commits are unknown semantic conflict
            num = len(list(k for k, v in json_info['Resolved_Commits'].items() if v['Semantic_conflict_status']
                           == ValueEnum.unknown))
            f.write('Number of commits are unknown semantic conflicts:' + str(num) + '\n')
            f.write('\n')


# Try block to detect AbnomralBehaviourError and serialization
try:
    # # debug code
    # test_1 = read_data('https://github.com/alibaba/fastjson')
    # test_1 = test_1['Resolved_Commits']
    # test_2 = read_data('https://github.com/alibaba/fastjson1')
    # test_2 = test_2['Resolved_Commits']
    # shared_items = {k: test_1[k] for k in test_1 if k in test_2 and test_1[k] == test_2[k]}
    # print(len(shared_items))
    # Read projects list
    with open(os.path.join(path_prefix, project_list_path), 'r') as fp:
        URL_list = [line.rstrip('\n') for line in fp]
    # Process each project in URL_list
    for idx, val in enumerate(URL_list):
        URL = val
        project_name = URL.split('/')[-1]
        # create logger to record project level info
        # create logger with 'script_logger'
        logger = logging.getLogger('script_logger')
        logger.setLevel(logging.INFO)
        # create file handler which logs even debug messages
        fh = logging.FileHandler(os.path.join(path_prefix, logger_path, project_name+'.log'))
        # fh = logging.FileHandler('script.log')
        fh.setLevel(logging.INFO)
        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        # add the handlers to the logger
        logger.addHandler(fh)
        # Change current path to workspace
        os.chdir(os.path.join(path_prefix, workspace))
        # if resume_project is enabled
        if resume_project:
            # Read project_record json file
            existed_project_record = read_data(URL)
            # If the resumed_project_record is not empty
            if existed_project_record:
                # Find existing data, still go over to find any missing commit
                logger.info('Resume project\t' + project_name)
            else:
                # not find existing data or empty
                # create a new project record
                # Update logger
                logger.info('Start project\t' + project_name)
        else:
            # create a new project record
            # Update logger
            logger.info('Start project\t' + project_name)
        # Ensure workspace is empty
        MergeMiner.clean_folder(os.path.join(path_prefix, workspace), logger)
        # Make a copy of the origin repository
        shutil.copytree(os.path.join(path_prefix, original_copy_path, project_name),
                        os.path.join(path_prefix, workspace, project_name))
        # Generate project information
        project_record = {'URL': URL, }
        # Check Ant/Maven/Gradlew
        if os.path.exists(os.path.join(path_prefix, workspace, project_name, 'build.xml')):
            # Type is Ant
            project_record['Type'] = 'Ant'
        elif os.path.exists(os.path.join(path_prefix, workspace, project_name, 'pom.xml')):
            # Type is Maven
            project_record['Type'] = 'Maven'
        elif os.path.exists(os.path.join(path_prefix, workspace, project_name, 'build.gradle')):
            # Type is Gradlew
            project_record['Type'] = 'Gradlew'
        else:
            # Don't belong to any type, remove from list
            logger.info('Project ' + URL + " doesn't belong to any type, removed")
            # Clean project_record
            project_record = []
            # Clean all files
            MergeMiner.clean_folder(os.path.join(path_prefix, workspace, project_name), logger)
            continue
        # Change current path to repository
        os.chdir(os.path.join(path_prefix, workspace, project_name))
        # Generate commit history
        MergeMiner.git_log(os.path.join(path_prefix, workspace, 'log_file'), logger)
        # Filter all merge commits (have two parents and have base version)
        commits_info = MergeMiner.filter_merge_commits(logger)
        project_record['Num_commits'] = commits_info['Num_commits']
        project_record['Num_merge_commits'] = commits_info['Num_merge_commits']
        project_record['Unresolved_commit_list'] = commits_info['merge_commits']
        # set project resolved commit list
        project_record['Resolved_Commits'] = {}
        #  Mark the status to working
        project_record['Process_status'] = 'working'
        # Process all unresolved commits
        # Debug code
        processed_commits_counter = 0
        while project_record['Unresolved_commit_list']:
            commit = project_record['Unresolved_commit_list'].pop()
            # if commit['Child'] != "30d1b53aa515b0a429fee814f9136145ee9886d5":
            #     continue
            if resume_project and existed_project_record:
                # if resume_project is enabled and the data exists
                match_commit = {k: v for k, v in existed_project_record['Resolved_Commits'].items()
                                if k == commit['Child']}
                if match_commit:
                    # find matched commit
                    # append the matched commit into resolved commit
                    project_record['Resolved_Commits'][commit['Child']] = match_commit.pop(commit['Child'])
                    # remove the matched commit from the existed project_record
                    del existed_project_record['Resolved_Commits'][commit['Child']]
                    continue
                else:
                    # cannot find matched commit. process as new commit
                    pass
            project_info = {'Project_name': project_name, 'Type': project_record['Type']}
            MergeMiner.process_commit(commit, project_info, logger)
            # append the processed commit into resolved commit
            project_record['Resolved_Commits'][commit['Child']] = commit
            processed_commits_counter += 1
            # continuously save data with 100 interval
            if processed_commits_counter > 5:
                save_data(URL)
        # Mark Process_status to be completed
        project_record['Process_status'] = 'completed'
        # Update logger
        logger.info('Finish project\t' + project_name)
        # save singe project json file
        save_data(URL)
        # close finish project log handle
        logger.removeHandler(fh)
        fh.close()
        # set a limit of projects can be processed
        if idx > 1000:
            break
    # Reach the end, all data should be already saved
    # Clean workspace
    MergeMiner.clean_folder(os.path.join(path_prefix, workspace), logger)
except MergeMiner.AbnormalBehaviourError as e:
    # Abnormal Behaviour happen, save current result
    print(str(e))
    # save singe project json file
    save_data(URL)
