from git import Repo
from pick import pick
import os

def chooseBranch():
    
    parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))

    repo = Repo(parent_dir)
    assert not repo.bare

    assert repo.remote().exists

    repo.remote().fetch()

    branch_names = []
    for r in repo.branches:
        branch_names.append(r.name)

    #branch_names.append('IVRA')
    #branch_names.append('Something')
    #print(branch_names)

    if len(branch_names) > 1:
        option = pick(branch_names, 'Pick a configuration')
        print(option)

        # TODO switch to branch

    print(f'Using configuration {repo.active_branch}')

chooseBranch()
