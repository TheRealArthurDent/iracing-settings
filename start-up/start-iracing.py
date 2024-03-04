from git import Repo
from pick import pick
import os

def chooseBranch():
    
    parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))

    repo = Repo(parent_dir)
    assert not repo.bare

    assert repo.remote().exists

    repo.remote().fetch()

    if len(repo.branches) > 1:
        option, index = pick(repo.branches, 'Pick a configuration')
        repo.branches[index].checkout()

    print(f'Using configuration {repo.active_branch}')

chooseBranch()
