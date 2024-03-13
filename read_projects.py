# Script to pre-select projects in github
import os
import logging

# create logger with 'script_logger'
logger = logging.getLogger('read_projects')
logger.setLevel(logging.INFO)
# create file handler which logs even debug messages
fh = logging.FileHandler('read_projects.log')
fh.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)

# Set path
unread_path_maven = 'dataset/maven'
unread_path_ant = 'dataset/ant'
unread_path_gradlew = 'dataset/gradlew'
# List initialization
maven = []
ant = []
gradlew = []

# list all files in dataset maven path
os.chdir(unread_path_maven)
maven_list = os.listdir('.')
for item in maven_list:
    logger.info("Detect project:\t" + item)
    if os.path.isdir(item):
        if os.path.isfile(item + '/URL'):
            # URL file does exist
            old_URL = [line.rstrip('\n') for line in open(item + '/URL')]
            if len(old_URL) == 1:
                maven.append(old_URL[0])
                logger.info("Add URL:\t" + old_URL[0])
            else:
                logger.error("Existed URL file contain multiple lines")
                exit(1)
        else:
            logger.error("URL file doesn't exist")
            exit(1)
    else:
        logger.error("File instead of folder detected")
        exit(1)
logger.info("Finish all projects")
os.chdir("../..")
with open("maven", "w") as f:
    for item in maven:
        f.write("%s\n" % item)

# list all files in dataset ant path
os.chdir(unread_path_ant)
ant_list = os.listdir('.')
for item in ant_list:
    logger.info("Detect project:\t" + item)
    if os.path.isdir(item):
        if os.path.isfile(item + '/URL'):
            # URL file does exist
            old_URL = [line.rstrip('\n') for line in open(item + '/URL')]
            if len(old_URL) == 1:
                ant.append(old_URL[0])
                logger.info("Add URL:\t" + old_URL[0])
            else:
                logger.error("Existed URL file contain multiple lines")
                exit(1)
        else:
            logger.error("URL file doesn't exist")
            exit(1)
    else:
        logger.error("File instead of folder detected")
        exit(1)
logger.info("Finish all projects")
os.chdir("../..")
with open("ant", "w") as f:
    for item in ant:
        f.write("%s\n" % item)

# list all files in dataset gradlew path
os.chdir(unread_path_gradlew)
gradlew_list = os.listdir('.')
for item in gradlew_list:
    logger.info("Detect project:\t" + item)
    if os.path.isdir(item):
        if os.path.isfile(item + '/URL'):
            # URL file does exist
            old_URL = [line.rstrip('\n') for line in open(item + '/URL')]
            if len(old_URL) == 1:
                gradlew.append(old_URL[0])
                logger.info("Add URL:\t" + old_URL[0])
            else:
                logger.error("Existed URL file contain multiple lines")
                exit(1)
        else:
            logger.error("URL file doesn't exist")
            exit(1)
    else:
        logger.error("File instead of folder detected")
        exit(1)
logger.info("Finish all projects")
os.chdir("../..")
with open("gradlew", "w") as f:
    for item in gradlew:
        f.write("%s\n" % item)
