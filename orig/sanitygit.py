"""
Perform sanity checks for Latex files in a git repository
"""

import re
import git
import os
import sys
import subprocess

try:
    from sanity import SanityDir
except ImportError:
    from langsci.sanity import SanityDir


def cloneorpull(url):
    """
    Make a git repository available locally. 
    
    The repo is cloned if not already available locally, otherwise, it is pull'ed.
    
    args:
      url (str): the url string of the repository. It can be either the html URL or the git url
      
    returns
      str: the file path to the local repo
      
    """
    m = re.search("langsci/([0-9]{2,}a?)", url)
    githubID = m.group(1)
    print("GitHub ID found:", githubID)
    giturl = "https://github.com/langsci/%s.git" % githubID
    gitdir = os.path.join(os.getcwd(), githubID)
    print("git repo is ", giturl)
    try:
        git.Repo.clone_from(giturl, gitdir)
        print("cloned")
    except git.exc.GitCommandError:
        print("repo already in file system. Pulling")
        cwd = os.getcwd()
        print(gitdir)
        os.chdir(gitdir)
        subprocess.call(["git", "pull"])
        os.chdir(cwd)
        print("pulled")
    return gitdir


if __name__ == "__main__":
    """
    usage: 
        python3 sanitygit.py https://www.github.com/langsci/42 
    """
    githuburl = sys.argv[1]
    ignorecodes = []
    try:
        ignorecodes = sys.argv[2:]
    except IndexError:
        pass
    d = cloneorpull(githuburl)
    lspdir = SanityDir(os.path.join(d, "."), ignorecodes)
    print(
        "checking %s"
        % "\n  ".join([""] + [f for f in lspdir.texfiles + lspdir.bibfiles])
    )
    lspdir.check()
    lspdir.printErrors()
    imgdir = SanityDir(os.path.join(d, "figures"), ignorecodes)
    imgdir.check()
    imgdir.printErrors()
