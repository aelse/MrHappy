from botplugin import BotPlugin
import logging
import time
import subprocess
import os
import re
import threading

class GitRepoMonitor(BotPlugin):

    timer = None
    git_repos = None
    notify_channel = None
    git_fetch_interval = 60

    config_options = {
        'git_repos': '/path/to/git/repos',
        'git_fetch_interval': str(git_fetch_interval),
        'notify_channel': '',
    }

    def setup(self, bot, options):
        self.bot = bot
        if options.has_key('git_repos'):
            self.git_repos = options['git_repos']
            logging.info('Monitoring git repositories under %s' % self.git_repos)
        if options.has_key('git_fetch_interval'):
            try:
                fetch_interval = int(options['git_fetch_interval'])
                self.git_fetch_interval = fetch_interval
                logging.info('Checking at %d second intervals.' % self.git_fetch_interval)
            except:
                pass
        if options.has_key('notify_channel'):
            self.notify_channel = options['notify_channel']
            logging.info('Sending notifications to %s' % self.notify_channel)

        if not self.timer and self.git_fetch_interval:
            logging.info('Setting git monitor timer to %d seconds.' % self.git_fetch_interval)
            self.timer = threading.Timer(self.git_fetch_interval, self.notify_channel_of_changes)
            self.timer.start()
        else:
            logging.warning('Not setting a git monitor timer.')

    def teardown(self):
        if self.timer:
            if self.timer.isAlive():
                self.timer.cancel()
            self.timer = None

    def notify_channel_of_changes(self):
        if self.git_repos and self.notify_channel:
            logging.info('Checking for changes in git repositories.')
            repos = discover_repos(self.git_repos)
            for repo in repos:
                logging.debug('Looking in repo %s' % repo)
                msgs = monitor_repo(self.git_repos, repo)   
                for msg in msgs:
                    self.bot.say_public(self.notify_channel, msg)
        else:
            logging.info('Skipping git repository checks.')

        # start a new timer if existing timer wasn't cancelled,
        # which may have happened while we were polling repos.
        if self.timer and self.git_fetch_interval:
            self.timer = threading.Timer(self.git_fetch_interval, self.notify_channel_of_changes)
            self.timer.start()
        else:
            logging.warning('Not setting a new git monitor timer.')


def monitor_repo(path_to_repos, repo):
    repo_name = re.sub('.git', '', repo)
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
                msgs.append('New commits in %s/%s:' % (repo_name, branch))
                for msg in gitlog.split('\n'):
                    msgs.append(' * ' + msg)
            m = re.search('\[new branch\]\s+(\S+)', line)
            if m: # a new branch
                branch = m.groups()[0]
                msgs.append('New branch %s/%s' % (repo_name, branch))
            m = re.search('\[new tag\]\s+(\S+)', line)
            if m: # a new tag
                tag = m.groups()[0]
                msgs.append('New tag %s/%s' % (repo_name, tag))
    return msgs

def discover_repos(path_to_repos):
    dirs = os.listdir(path_to_repos)
    repos = []
    for d in dirs:
        path = '/'.join((path_to_repos, d))
        try:
            # if exception not raised return code 0 and it is a git dir.
            subprocess.check_call(['git', 'rev-parse', '--git-dir'], cwd=path)
        except:
            continue
        repos.append(d)
    return repos

def monitor_repos(path_to_repos):
    repos = discover_repos(path_to_repos)
    for repo in repos:
        msgs = monitor_repo(path_to_repos, repo)
        if len(msgs) > 0:
            for msg in msgs:
                print msg

def monitor_repos_after_delay(path_to_repos, delay):
    timer = threading.Timer(delay, monitor_repos)
    timer.start()
    while timer.isAlive():
        time.sleep(1)

if __name__ == "__main__":
    import sys
    monitor_repos(sys.argv[1])
