# Script to pre-select projects in github
# 1. belong to Top 1K starred projects
# 2. belong to Ant/Maven/Gradlew
# 3. have at least one merge scenario (two parent commits)
# 4. latest version can compile and test success within 5 minutes
import os
import logging
from pathlib import Path
import shutil
import time
import subprocess
import json
# import other user module
import MergeMiner
from EnumEncoder import EnumEncoder, as_enum
from ValueEnum import ValueEnum

# clone repositories from local copy
mode = 'local'
# clone repositories from github
# mode = 'github'


# Set path
path_prefix = '/home/ppp/Research_Projects/Merge_Conflicts'
output_path = 'Script/github_star_projects/repository_snapshot/final_list.txt'
Top_1K_path = 'Script/github_star_projects/repository_snapshot/Top_1K.json'
# Filter_result_path = 'Script/github_star_projects/repository_snapshot/valid_list.json'
Top_1K_checked_path = 'Script/github_star_projects/repository_snapshot/Top_1K_checked.json'
processed_index_path = 'Script/github_star_projects/repository_snapshot/processed_index'
workspace = 'Resource/workspace'
logger_path = 'Script/github_star_projects/filter_repository.log'
# Set the longest waiting time to wait for a task to execute (Unit: minutes)
MAX_WAITINGTIME_COMPILE = 5*60
MAX_WAITINGTIME_TEST = 10*60
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


# Filter start at 04/28/2020
# All data are stored in repository_snapshot folder
# def save_data(result):
#     with open(os.path.join(path_prefix, Filter_result_path), 'w') as outfile:
#         json.dump(result, outfile, cls=EnumEncoder)


def read_data(path):
    if os.path.exists(path):
        with open(path, 'r') as infile:
            # nonlocal project_record
            return json.load(infile, object_hook=as_enum)
    else:
        return []


def save_checked_list(result):
    with open(os.path.join(path_prefix, Top_1K_checked_path), 'w') as outfile:
        json.dump(result, outfile, cls=EnumEncoder)


def write_data(path):
    with open(path, 'w') as f:
        # data_list = [item['URL'] for item in Top_1K_checked]
        data_list = [item['Compilation_timeout'] for item in Top_1K_checked]
        for item in data_list:
            f.write("%s\n" % item)


def folder_size(path):
    total = 0
    for entry in os.scandir(path):
        if entry.is_file() and not entry.is_symlink():
            total += entry.stat().st_size
        elif entry.is_dir():
            total += folder_size(entry.path)
    return total


# Compile latest version
def run_compile(compile_cmd, logger):
    try:
        proc = subprocess.Popen(compile_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        outs, errs = proc.communicate(timeout=MAX_WAITINGTIME_COMPILE)
        if proc.returncode == 0:
            # Succeed to run compilation command in latest version
            # Update logger
            logger.info("latest version compilation succeed")
            return 1
        else:
            # Failed to run compile command in latest version
            # Update logger
            logger.info("latest version compilation failed")
            return -1
    except subprocess.TimeoutExpired:
        # Terminate the unfinished process
        proc.terminate()
        # Timeout occur
        # Update logger
        logger.info("latest version compilation fail to finish in time")
        return 0
    finally:
        pass


# Test latest version
def run_test(test_cmd, logger):
    try:
        proc = subprocess.Popen(test_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        outs, errs = proc.communicate(timeout=MAX_WAITINGTIME_TEST)
        if proc.returncode == 0:
            # Succeed to run test command in latest version
            # Update logger
            logger.info("latest version test succeed")
            return 1
        else:
            # Failed to run test command in latest version
            # Update logger
            logger.info("latest version test failed")
            return -1
    except subprocess.TimeoutExpired:
        # Terminate the unfinished process
        proc.terminate()
        # Timeout occur
        # Update logger
        logger.info("latest version test fail to finish in time")
        return 0
    finally:
        pass


def check_ineligible_build_tool():
    Top_1K_checked.append({'URL': URL,
                           'Project_name': project_name,
                           'Ant': ValueEnum.false,
                           'Maven': ValueEnum.false,
                           'Gradlew': ValueEnum.false,
                           'Merge_Commits': ValueEnum.unknown,
                           'Compilation_success': ValueEnum.unknown,
                           'Compilation_timeout': ValueEnum.unknown,
                           'Test_success': ValueEnum.unknown,
                           'Test_timeout': ValueEnum.unknown})


def check_ineligible_merge_commit():
    if Type == 'Ant':
        Top_1K_checked.append({'URL': URL,
                               'Project_name': project_name,
                               'Ant': ValueEnum.true,
                               'Maven': ValueEnum.false,
                               'Gradlew': ValueEnum.false,
                               'Merge_Commits': ValueEnum.false,
                               'Compilation_success': ValueEnum.unknown,
                               'Compilation_timeout': ValueEnum.unknown,
                               'Test_success': ValueEnum.unknown,
                               'Test_timeout': ValueEnum.unknown})
    elif Type == 'Maven':
        Top_1K_checked.append({'URL': URL,
                               'Project_name': project_name,
                               'Ant': ValueEnum.false,
                               'Maven': ValueEnum.true,
                               'Gradlew': ValueEnum.false,
                               'Merge_Commits': ValueEnum.false,
                               'Compilation_success': ValueEnum.unknown,
                               'Compilation_timeout': ValueEnum.unknown,
                               'Test_success': ValueEnum.unknown,
                               'Test_timeout': ValueEnum.unknown})
    elif Type == 'Gradlew':
        Top_1K_checked.append({'URL': URL,
                               'Project_name': project_name,
                               'Ant': ValueEnum.false,
                               'Maven': ValueEnum.false,
                               'Gradlew': ValueEnum.true,
                               'Merge_Commits': ValueEnum.false,
                               'Compilation_success': ValueEnum.unknown,
                               'Compilation_timeout': ValueEnum.unknown,
                               'Test_success': ValueEnum.unknown,
                               'Test_timeout': ValueEnum.unknown})
    else:
        raise MergeMiner.AbnormalBehaviourError("Invalid Build tool type")


def check_ineligible_compilation_fail():
    if Type == 'Ant':
        Top_1K_checked.append({'URL': URL,
                               'Project_name': project_name,
                               'Ant': ValueEnum.true,
                               'Maven': ValueEnum.false,
                               'Gradlew': ValueEnum.false,
                               'Merge_Commits': ValueEnum.true,
                               'Compilation_success': Compilation_success,
                               'Compilation_timeout': Compilation_timeout,
                               'Test_success': ValueEnum.unknown,
                               'Test_timeout': ValueEnum.unknown})
    elif Type == 'Maven':
        Top_1K_checked.append({'URL': URL,
                               'Project_name': project_name,
                               'Ant': ValueEnum.false,
                               'Maven': ValueEnum.true,
                               'Gradlew': ValueEnum.false,
                               'Merge_Commits': ValueEnum.true,
                               'Compilation_success': Compilation_success,
                               'Compilation_timeout': Compilation_timeout,
                               'Test_success': ValueEnum.unknown,
                               'Test_timeout': ValueEnum.unknown})
    elif Type == 'Gradlew':
        Top_1K_checked.append({'URL': URL,
                               'Project_name': project_name,
                               'Ant': ValueEnum.false,
                               'Maven': ValueEnum.false,
                               'Gradlew': ValueEnum.true,
                               'Merge_Commits': ValueEnum.true,
                               'Compilation_success': Compilation_success,
                               'Compilation_timeout': Compilation_timeout,
                               'Test_success': ValueEnum.unknown,
                               'Test_timeout': ValueEnum.unknown})
    else:
        raise MergeMiner.AbnormalBehaviourError("Invalid Build tool type")


def check_eligible():
    if Type == 'Ant':
        Top_1K_checked.append({'URL': URL,
                               'Project_name': project_name,
                               'Ant': ValueEnum.true,
                               'Maven': ValueEnum.false,
                               'Gradlew': ValueEnum.false,
                               'Merge_Commits': ValueEnum.true,
                               'Compilation_success': ValueEnum.true,
                               'Compilation_timeout': ValueEnum.false,
                               'Test_success': ValueEnum.unknown,
                               'Test_timeout': ValueEnum.unknown})
    elif Type == 'Maven':
        Top_1K_checked.append({'URL': URL,
                               'Project_name': project_name,
                               'Ant': ValueEnum.false,
                               'Maven': ValueEnum.true,
                               'Gradlew': ValueEnum.false,
                               'Merge_Commits': ValueEnum.true,
                               'Compilation_success': ValueEnum.true,
                               'Compilation_timeout': ValueEnum.false,
                               'Test_success': ValueEnum.unknown,
                               'Test_timeout': ValueEnum.unknown})
    elif Type == 'Gradlew':
        Top_1K_checked.append({'URL': URL,
                               'Project_name': project_name,
                               'Ant': ValueEnum.false,
                               'Maven': ValueEnum.false,
                               'Gradlew': ValueEnum.true,
                               'Merge_Commits': ValueEnum.true,
                               'Compilation_success': ValueEnum.true,
                               'Compilation_timeout': ValueEnum.false,
                               'Test_success': ValueEnum.unknown,
                               'Test_timeout': ValueEnum.unknown})
    else:
        raise MergeMiner.AbnormalBehaviourError("Invalid Build tool type")


# This is for special case need manually revise
def check_special():
    Top_1K_checked.append({'URL': URL,
                           'Project_name': project_name,
                           'Ant': ValueEnum.unknown,
                           'Maven': ValueEnum.unknown,
                           'Gradlew': ValueEnum.unknown,
                           'Merge_Commits': ValueEnum.unknown,
                           'Compilation_success': ValueEnum.unknown,
                           'Compilation_timeout': ValueEnum.unknown,
                           'Test_success': ValueEnum.unknown,
                           'Test_timeout': ValueEnum.unknown})


try:
    Special_list = ['https://github.com/aosp-mirror/platform_frameworks_base',
                    'https://github.com/AndroidBootstrap/android-bootstrap',
                    'https://github.com/ZXZxin/ZXBlog',
                    'https://github.com/bisq-network/bisq',
                    'https://github.com/psaravan/JamsMusicPlayer',
                    'https://github.com/ZHENFENG13/spring-boot-projects',
                    'https://github.com/jersey/jersey',
                    'https://github.com/edmodo/cropper',
                    'https://github.com/Dromara/hmily',
                    'https://github.com/stylefeng/Guns',
                    'https://github.com/chenupt/SpringIndicator']
    Top_1K = read_data(os.path.join(path_prefix, Top_1K_path))
    # resume existing data
    # filter_result = read_data(os.path.join(path_prefix, Filter_result_path))
    Top_1K_checked = read_data(os.path.join(path_prefix, Top_1K_checked_path))
    # # Temporary code to read Whole_Data_List
    # with open(os.path.join(path_prefix, "Script/github_star_projects/repository_snapshot/Whole_Data_List")) as f:
    #     new_seq = f.read().splitlines()
    # search_db = [{'URL': item['URL'], 'stars':item['stars']} for item in filter_result]
    # index_seq = [search_db[[item['URL'] for item in search_db].index(item)]['stars'] for item in new_seq]
    # # Temporary code to write result
    write_data(os.path.join(path_prefix, output_path))
    # check the latest processed project index
    with open(os.path.join(path_prefix, processed_index_path), 'r') as f:
        num_index = f.readline()
    num_index = int(num_index)
    # Change current path to workspace
    os.chdir(os.path.join(path_prefix, workspace))
    # Clean the workspace folder
    # time.sleep(90)
    MergeMiner.clean_folder(os.path.join(path_prefix, workspace), logger)
    for project in Top_1K:
        # Start with the last processed index (index starts from 0)
        if Top_1K.index(project) < num_index:
            continue
        URL = project['URL']
        # if URL in [item["URL"] for item in filter_result]:
        #     # if this project has been processed, skip this project
        #     continue
        project_name = URL.split('/')[-1]
        # Update logger
        logger.info('Process project ' + project_name)
        # Check special case
        if URL in Special_list:
            logger.info('Special case, skip this project')
            check_special()
            # save all data
            save_checked_list(Top_1K_checked)
            # Save the processed index
            with open(os.path.join(path_prefix, processed_index_path), 'w') as f:
                f.write(str(Top_1K.index(project)))
            continue
        # stars = project['stargazers_count']
        # API_size = project['size']
        MergeMiner.git_clone(URL, project_name, logger)
        # Reset to the specific commit at experiment
        os.chdir(project_name)
        MergeMiner.git_reset_commit(project['latest_commit'], logger)
        # Folder_size = round(folder_size(project_name)/1024)
        # Git_size = round(folder_size(os.path.join(project_name, '.git'))/1024)
        if os.path.exists(os.path.join("build.xml")):
            Type = 'Ant'
            compile_cmd = 'ant clean build'
            test_cmd = 'ant clean test'
            # Update logger
            logger.info('Belong to Ant')
        elif os.path.exists(os.path.join("pom.xml")):
            Type = 'Maven'
            compile_cmd = 'mvn clean compile'
            test_cmd = 'mvn clean test'
            # Update logger
            logger.info('Belong to Maven')
        elif os.path.exists(os.path.join("build.gradle")):
            Type = 'Gradlew'
            compile_cmd = './gradlew clean assemble'
            test_cmd = './gradlew clean test'
            # Update logger
            logger.info('Belong to Gradlew')
        else:
            # Don't belong to Ant/Maven/Gradlew, skip this project
            # Update logger
            logger.info("Don't belong to any type, skip this project")
            # Mark this project not eligible because of missing build tool
            check_ineligible_build_tool()
            # save all data
            save_checked_list(Top_1K_checked)
            # Save the processed index
            with open(os.path.join(path_prefix, processed_index_path), 'w') as f:
                f.write(str(Top_1K.index(project)))
            # Change current path to workspace
            os.chdir(os.path.join(path_prefix, workspace))
            # Clean the workspace folder
            # time.sleep(90)
            MergeMiner.clean_folder(os.path.join(path_prefix, workspace), logger)
            continue
        # Find at least one merge commit to be eligible
        MergeMiner.git_log(os.path.join(path_prefix, workspace, 'log_file'), logger)
        Merge_Scenario = False
        with open(os.path.join(path_prefix, workspace, 'log_file'), 'r') as f:
            while True:
                commit_line = f.readline()
                if not commit_line:
                    break
                child = commit_line[-1].replace('\n', '')
                parent_line = f.readline().split(' ')
                if len(parent_line) == 3:
                    # find merge scenario, go to next step
                    logger.info('Find merge commit ' + child)
                    Merge_Scenario = True
                    break
        if not Merge_Scenario:
            # if there is no merge scenario, skip this project
            # Update logger
            logger.info('No merge scenario found, skip this project')
            # Mark this project not eligible because of missing merge commit
            check_ineligible_merge_commit()
            # save all data
            save_checked_list(Top_1K_checked)
            # Save the processed index
            with open(os.path.join(path_prefix, processed_index_path), 'w') as f:
                f.write(str(Top_1K.index(project)))
            # Change current path to workspace
            os.chdir(os.path.join(path_prefix, workspace))
            # Clean the workspace folder
            # time.sleep(90)
            MergeMiner.clean_folder(os.path.join(path_prefix, workspace), logger)
            continue
        # Till now, we confirm that we will record this project
        Compilation_success = ValueEnum.unknown
        Compilation_timeout = ValueEnum.unknown
        Test_success = ValueEnum.unknown
        Test_timeout = ValueEnum.unknown
        # Compile the latest version
        result = run_compile(compile_cmd, logger)
        if result == 1:
            # compilation succeed
            Compilation_success = ValueEnum.true
            Compilation_timeout = ValueEnum.false
        elif result == -1:
            # compilation fail
            Compilation_success = ValueEnum.false
            Compilation_timeout = ValueEnum.false
        elif result == 0:
            # compilation time out
            Compilation_success = ValueEnum.unknown
            Compilation_timeout = ValueEnum.true
        else:
            raise MergeMiner.AbnormalBehaviourError("wrong return value from run_compile")
        # We don't need this step
        # # if compilation succeed, continue to test
        # if Compilation_success == ValueEnum.true:
        #     result = run_test(test_cmd, logger)
        #     if result == 1:
        #         # test succeed
        #         Test_success = ValueEnum.true
        #         Test_timeout = ValueEnum.false
        #     elif result == -1:
        #         # test fail
        #         Test_success = ValueEnum.false
        #         Test_timeout = ValueEnum.false
        #     elif result == 0:
        #         # test time out
        #         Test_success = ValueEnum.unknown
        #         Test_timeout = ValueEnum.true
        #     else:
        #         raise MergeMiner.AbnormalBehaviourError("wrong return value from run_test")
        # Change current path to workspace
        os.chdir(os.path.join(path_prefix, workspace))
        # Remove this part, instead of a list of all valid projects.
        # We return the more detailed version, whole 1K projects marked with all attributes.
        # # Record the information into the filter_result
        # filter_result.append({'URL': URL,
        #                       'index': Top_1K.index(project),
        #                       'stars': stars,
        #                       'API_size': API_size,
        #                       'Folder_size': Folder_size,
        #                       'Git_size': Git_size,
        #                       'Type': Type,
        #                       'Compilation_success': Compilation_success,
        #                       'Compilation_timeout': Compilation_timeout,
        #                       'Test_success': Test_success,
        #                       'Test_timeout': Test_timeout})
        if Compilation_success == ValueEnum.true:
            # Mark this project eligible
            check_eligible()
        else:
            check_ineligible_compilation_fail()
        # save all data
        # save_data(filter_result)
        save_checked_list(Top_1K_checked)
        # Save the processed index
        with open(os.path.join(path_prefix, processed_index_path), 'w') as f:
            f.write(str(Top_1K.index(project)))
        # Put here because clean may cause error, so put at last
        # Clean the workspace folder
        time.sleep(90)
        MergeMiner.clean_folder(os.path.join(path_prefix, workspace), logger)
    # save_data(filter_result)
except MergeMiner.AbnormalBehaviourError as e:
    # Abnormal Behaviour happen, save current result
    print(str(e))
    # save_data(filter_result)
except Exception as e:
    print(str(e))
    # save_data(filter_result)
