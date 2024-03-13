# Source Code of TOSEM

**Multiple files contain various paths. Remember to modify paths setting before running scripts.**

## Prepare dataset
1. Get the top 1K Java repositories in Github based on stargaze ranking.
   For exmample

   WebPage

   https://github.com/search?l=Java&o=desc&q=stars%3A%3E2000&s=stars&type=Repositories

   API

   https://api.github.com/search/repositories?q=stars%3A%3E2000+language:java&sort=stars&per_page=100&page=1

   This is done in `save_repositories.py`. Results stored in Top_1K.json

   Our version is based on ranking results on 2020. It may be different from current status.

3. Pre-select eligible repositories.
   This is done in `filter_repositories.py`. Results stored in Top_1K_checked.json   

## Collect conflicts
   Iterate eligible repositories to collect conflicts.

   This is done in `script.py`. We extract all urls from Top_1K_checked.json in previous step to compose valid_list. It just need a little change of code if you want to directly use previous json file.
   
   We store all eligible repositories locally at `original_copy_path`. If you need to skip this, please modify the corresponding part according.

   Results will be stored in `project_record.json`


