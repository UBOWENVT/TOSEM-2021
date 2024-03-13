# Script to extract textual conflicts in project_record
import os
from pathlib import Path
import shutil
import json
# import another user module
from enum import Enum


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
# data_path = '/home/ppp/Research_Projects/Merge_Conflicts/Script/github_star_projects/Experiment/Top100/projects_record/'
data_path = '/home/ppp/Research_Projects/Merge_Conflicts/Script/github_star_projects/Experiment/Whole_Data/'
project_name = 'spring-boot-api-project-seed'
project_record = view_data(data_path+project_name)
commits_with_textual_conflicts = [item for item in project_record['Resolved_Commits'].values() if item['Textual_conflict_status'] == ValueEnum.true]
commits_with_syntactic_conflicts = [item for item in project_record['Resolved_Commits'].values() if item['Syntactic_conflict_status'] == ValueEnum.true]
commits_with_semantic_conflicts = [item for item    in project_record['Resolved_Commits'].values() if item['Semantic_conflict_status'] == ValueEnum.true]
child_commit = [item['Child'] for item in commits_with_textual_conflicts]
if commits_with_textual_conflicts:
    print("We find textual conflict commits")
else:
    print("We don't find any textual conflict commit")
