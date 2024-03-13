# Script to pre-select projects in github
import os
import logging
import requests
import shutil
import subprocess
# import another user module
import MergeMiner
from ValueEnum import ValueEnum

# clone repositories from local copy
mode = 'local'
# clone repositories from github
# mode = 'github'


# Set path
path_prefix = '/home/ppp/Research_Projects/Merge_Conflicts'
project_list_path = 'Script/github_star_projects/URL_list'
valid_project_list_path = 'Script/github_star_projects/valid_list'
# project_list_path = 'Script/github_star_projects/debug_list'
# project_list_path = 'Script/github_star_projects/switch_order'
project_record_path = 'Script/github_star_projects/project_record.json'
project_record_folder_path = 'Script/github_star_projects/project_record'
workspace = 'Resource/workspace'
original_copy_path = 'Resource/Original_copy_projects'
logger_path = 'Script/github_star_projects/script.log'
report_path = 'Script/github_star_projects/report'
# Global variable (access with module)
project_record = []


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

# Store all copy of repositories at 02/10/2020
with open(os.path.join(path_prefix, project_list_path), 'r') as fp:
    URL_list = [line.rstrip('\n') for line in fp]
    valid_list = []
    for idx, val in enumerate(URL_list):
        URL = val
        project_name = URL.split('/')[-1]
        # check URL validity
        if mode == 'github':
            response = requests.get(URL)
            if response.status_code < 400:
                logger.info("%s URL is valid", URL)
            else:
                logger.error("Repository unavailable\t" + URL)
                continue
        elif mode == 'local':
            # check repository existence
            if os.path.isdir(os.path.join(path_prefix, original_copy_path, project_name)):
                logger.info("%s URL is valid", URL)
            else:
                logger.error("Repository unavailable\t" + URL)
                continue
        else:
            raise MergeMiner.AbnormalBehaviourError("Wrong mode when download repositories")
        # Change current path to workspace
        os.chdir(os.path.join(path_prefix, workspace))
        # Ensure workspace is empty
        MergeMiner.clean_folder(os.path.join(path_prefix, workspace), logger)
        # Download project
        if mode == 'github':
            MergeMiner.git_clone(URL, project_name, logger)
        elif mode == 'local':
            shutil.copytree(os.path.join(path_prefix, original_copy_path, project_name),
                            os.path.join(path_prefix, workspace, project_name))
        else:
            raise MergeMiner.AbnormalBehaviourError("Wrong mode when download repositories")
        # Check Ant/Maven/Gradlew
        compile_cmd = []
        if os.path.exists(os.path.join(path_prefix, workspace, project_name, "build.xml")):
            # Belong to Ant
            compile_cmd = 'ant clean build'
        elif os.path.exists(os.path.join(path_prefix, workspace, project_name, "pom.xml")):
            # Belong to Maven
            compile_cmd = 'mvn clean compile'
        elif os.path.exists(os.path.join(path_prefix, workspace, project_name, "build.gradle")):
            # Belong to Gradlew
            compile_cmd = './gradlew clean assemble'
        else:
            # Don't belong to any type, remove from list
            logger.info("Project " + URL + " doesn't belong to any type, removed")
            continue
        # Compile latest version
        # Change current path to project folder in workspace
        os.chdir(os.path.join(path_prefix, workspace, project_name))
        try:
            if subprocess.run(compile_cmd, shell=True, timeout=MergeMiner.MAX_WAITINGTIME_COMPILE).returncode == 0:
                # Update logger
                logger.info("Project " + project_name + " successfully compiled latest version")
                # Succeed to run compilation command in latest version
                valid_list.append(URL)
                if mode == 'github':
                    # Make a copy of the origin repository
                    if os.path.isdir(os.path.join(path_prefix, original_copy_path, project_name)):
                        raise MergeMiner.AbnormalBehaviourError('Repository already exists in destination')
                    else:
                        shutil.copytree(os.path.join(path_prefix, workspace, project_name),
                                        os.path.join(path_prefix, original_copy_path, project_name))
            else:
                # Failed to run compile command in latest version
                # Update logger
                logger.info("Project " + project_name + " failed to compile latest version")
                continue
        except subprocess.TimeoutExpired:
            # Timeout occur
            # Update logger
            logger.info("Project " + project_name + " failed to compile latest version in time")
            continue
        finally:
            pass


with open(os.path.join(path_prefix, valid_project_list_path), 'w') as f:
    for item in valid_list:
        f.write(item + '\n')
