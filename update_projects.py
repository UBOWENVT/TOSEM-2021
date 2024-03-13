# Script to pre-select projects in github
import os
import logging
import subprocess
import shutil
from pathlib import Path


def save_data():
    with open("maven_list", "w") as f:
        for item in maven:
            f.write("%s\n" % item)
    with open("ant_list", "w") as f:
        for item in ant:
            f.write("%s\n" % item)
    with open("gradlew_list", "w") as f:
        for item in gradlew:
            f.write("%s\n" % item)
    with open("scanned_list", "w") as f:
        for item in scanned:
            f.write("%s\n" % item)


def rmtree_try(rm_name, rm_logger):
    try:
        shutil.rmtree(rm_name)
    except shutil.Error:
        rm_logger.error("remove folder error occurred")
        save_data()
        exit(1)
    except Exception:
        rm_logger.error("Unkown error")
        save_data()
        exit(1)


def update():
    URL_list = []
    project_list = os.listdir('.')
    for project_name in project_list:
        os.chdir(project_name)
        file_URL = Path('URL')
        if file_URL.is_file():
            with open('URL') as fp:
                stored_URL = [line.rstrip('\n') for line in fp]
            if len(stored_URL) == 1:
                logger.info("URL is " + stored_URL[0])
                URL_list.append(stored_URL[0])
                name = stored_URL[0].split('/')[-1]
                os.chdir('..')
                rmtree_try(name, logger)
                cmd = ["git", "clone", stored_URL[0]]
                try:
                    status = subprocess.run(cmd, shell=False, timeout=180, check=True).returncode
                except subprocess.TimeoutExpired:
                    rmtree_try(name, logger)
                    logger.info("Timeout occur")
                    continue
                except subprocess.CalledProcessError:
                    logger.info("Cannot download the repository")
                    rmtree_try(name, logger)
                    continue
                else:
                    if status != 0:
                        logger.error("git clone failed without catching exception")
                        # save data at first
                        save_data()
                        exit(1)
                    else:
                        os.chdir(name)
                        with open("URL", "w") as f:
                            f.write("%s" % stored_URL[0])
                        os.chdir('..')
                logger.info("Downloading repository succeed")
            else:
                logger.error("Multiple line of URLs found")
                os.chdir('..')
        else:
            logger.error("URL file doesn't exist")
            os.chdir('..')
    os.chdir('..')
    return URL_list


# create logger with 'script_logger'
logger = logging.getLogger('update_project_logger')
logger.setLevel(logging.INFO)
# create file handler which logs even debug messages
fh = logging.FileHandler('update_project.log')
fh.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
# Set path

# List initialization
scanned = []
maven = []
ant = []
gradlew = []
# 1. scan all projects in maven
os.chdir("maven")
maven = update()
# 2. scan all projects in gradle
os.chdir("gradlew")
gradlew = update()
# 3. scan all projects in ant
os.chdir("ant")
ant = update()
# 4. combine all list into scanned
scanned = maven + gradlew + ant
save_data()