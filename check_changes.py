import subprocess
import os
from pathlib import Path


def has_python_file_changed(repository_name:str):
    # we check if a python file has changed since the last pull
    # we go to the repository
    os.chdir(repository_name)
    # we get the last commit
    fetch = subprocess.Popen(["git", "fetch"], stdout=subprocess.PIPE)
    fetch.wait()
    # we get the last commit of the remote repository
    last_commit = subprocess.check_output(["git", "rev-parse", "FETCH_HEAD"]).strip()
    # we get the last commit of the local repository
    local_last_commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip()
    # we compare the two commits
    # compare the SHAs to see if the Python file has changed
    files_changed = subprocess.check_output(["git", "diff", "--name-only", last_commit, local_last_commit],encoding='utf-8').splitlines()
    print(files_changed)
    for file in files_changed:
        print([char for char in file])
        if file.endswith(".py"):
            return True
    return False

print(has_python_file_changed("C:/Users/jules/Documents/Git/BenchSite"))