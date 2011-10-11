import logging
import time
import subprocess
import os
import re

def monitor_repo(path_to_repos, repo):
    path = '/'.join((path_to_repos, repo))
    os.chdir(path)
    msgs = []
    git_output = subprocess.Popen(['git', 'fetch'],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        close_fds=True).communicate()[0]
    for line in git_output.split('\n'):
        if re.search('->', line):
            logging.debug('Found change %s: Got %s\n' % (repo, line))
            m = re.search('^\s*([0-9a-f]+\.\.[0-9a-f]+)\s+([\S]+)', line)
            if m: # a change to existing branch
                commit = m.groups()[0]
                branch = m.groups()[1]
                gitlog = subprocess.Popen(
                    ['git', 'log', commit, '--pretty=format:%s (%an)'],
                    stdout=subprocess.PIPE).communicate()[0]
                msgs.append('New commits in %s/%s:' % (repo, branch))
                for msg in gitlog.split('\n'):
                    msgs.append(' * ' + msg)
            m = re.search('\[new branch\]\s+(\S+)', line)
            if m: # a new branch
                branch = m.groups()[0]
                msgs.append('New branch %s/%s' % (repo, branch))
            m = re.search('\[new tag\]\s+(\S+)', line)
            if m: # a new tag
                tag = m.groups()[0]
                msgs.append('New tag %s/%s' % (repo, tag))
    return msgs

def monitor_repos(path_to_repos):
    dirs = os.listdir(path_to_repos)
    for d in dirs:
        path = '/'.join((path_to_repos, d, '.git'))
        try:
            os.stat(path)
        except:
            continue
        msgs = monitor_repo(path_to_repos, d)
        if len(msgs) > 0:
            for msg in msgs:
                print msg

if __name__ == "__main__":
    import sys
    monitor_repos(sys.argv[1])
