# Script to do statistics in project_record
import os
from pathlib import Path
import shutil
import json
# import another user module
from enum import Enum
import MergeMiner

class ValueEnum(Enum):
    false = 1
    true = 2
    unknown = 3


class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if obj in ValueEnum:
            return {'__enum__': str(obj)}
        return json.JSONEncoder.default(self, obj)


def as_enum(data):
    if '__enum__' in data:
        name, member = data['__enum__'].split('.')
        return getattr(ValueEnum, member)
    else:
        return data


def view_data(path):
    if os.path.exists(path):
        with open(path, 'r') as infile:
            # nonlocal project_record
            return json.load(infile, object_hook=as_enum)
    else:
        return {}


# Specify the path pointing to the json file
data_path = '/home/ppp/Research_Projects/Merge_Conflicts/Script/github_star_projects/Experiment/Whole_Data/'
project_name = []
project_record = []
statistics = []
unfinish_projects = []
try:
    for filename in os.listdir(data_path):
        file_path = os.path.join(data_path, filename)
        if os.path.isfile(file_path):
            project_record = view_data(file_path)
            # if project_record['Unresolved_commit_list']:
            print(filename)
            if project_record['Process_status'] == 'working':
                # Unresolved commit exists
                unfinish_projects.append(project_record)
            else:
                # Count number of commits
                # project_info[""]
                textual_conflict_num = len([item for item in project_record['Resolved_Commits'].values() if
                                            item['Textual_conflict_status'] == ValueEnum.true])
                syntactic_conflict_num = len([item for item in project_record['Resolved_Commits'].values() if
                                              item['Syntactic_conflict_status'] == ValueEnum.true])
                semantic_conflict_num = len([item for item in project_record['Resolved_Commits'].values() if
                                            item['Semantic_conflict_status'] == ValueEnum.true])
                project_info = {'URL': project_record['URL'],
                                'Project_Name': filename,
                                'Type': project_record['Type'],
                                'Num_of_commits': project_record['Num_commits'],
                                'Num_of_ merged_commits': project_record['Num_merge_commits'],
                                'Textual_conflict_commit_num': textual_conflict_num,
                                'Syntactic_conflict_commit_num': syntactic_conflict_num,
                                'Semantic_conflict_commit_num': semantic_conflict_num}
                statistics.append(project_info)
        elif os.path.isdir(file_path):
            raise MergeMiner.AbnormalBehaviourError("No folder should exist")
except Exception as e:
    print(str(e))
    exit(1)
# commits_with_textual_conflicts = [item for item in project_record['Resolved_Commits'].values() if item['Textual_conflict_status'] == ValueEnum.true]
# if commits_with_textual_conflicts:
#     print("We find textual conflict commits")
# else:
#     print("We don't find any textual conflict commit")
print(unfinish_projects)
print(statistics)
