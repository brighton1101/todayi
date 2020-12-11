from datetime import datetime
import subprocess

from todayi.remote.base import Remote
from todayi.util.fs import path, InvalidDirectoryError


class GitRemote(Remote):
    """
    A rough git remote implementation to use a git repository as
    a remote to backup your data.

    :param local_backend_path: path to local backend dir
    :type local_backend_path: str
    :param remote_uri: the uri for the remote to push/pull from
    :type remote_uri: str
    """

    _remote_origin_exists = "already exists"

    _no_init_commit = "do not have the initial commit yet"

    def __init__(self, local_backend_path: str, remote_uri: str):
        self._local_backend_path = local_backend_path
        self._remote_uri = remote_uri
        self._init_checked = False
        self._origin_checked = False

    @property
    def initialized(self):
        if self._init_checked == False:
            self._init_repo()
        if self._origin_checked == False:
            self._init_origin()
        return True

    def push(self, backup: bool = False):
        """
        Pushes to git origins master branch. By
        default will force push and overwrite origins
        commit history with local history.

        :param backup: whether or not to backup on the remote
        :type backup: bool
        """
        assert self.initialized == True
        if backup == True:
            raise NotImplementedError(
                'Backup logic not configured for GitRemote.push'
            )
        else:
            self._stage_changes()
            self._commit_changes()
            self._push_changes(force=True)

    def pull(self, backup: bool = False):
        """
        Pulls from git origins master branch. By
        default discards any local changes, but will
        rollback if there is a problem fetching or
        resetting from remote.

        :param backup: whether or not to backup locally
        :type backup: bool
        """
        assert self.initialized == True
        if backup == True:
            raise NotImplementedError(
                'Backup logic not configured for GitRemote.pull'
            )
        else:
            self._stash_changes()
            try:
                self._reset_from_origin()
            except Exception as e:
                self._rollback_from_stash()
                raise e

    def _init_repo(self):
        backend_path = path(self._local_backend_path)
        if not backend_path.exists() or not backend_path.is_dir():
            raise InvalidDirectoryError('Could not find backend directory')
        git_subdir = path(backend_path, '.git')
        if not git_subdir.exists():
            init_call = self._git_call('init')
            if init_call.returncode != 0:
                raise GitException('Could not initialize repo in {}'.format(
                    self._local_backend_path
                ))
        self._init_checked = True

    def _init_origin(self):
        check_origin_call = self._git_call('config', '--get', 'remote.origin.url')
        check_origin_out = check_origin_call.stdout.decode('utf-8').strip()
        print(check_origin_out)
        if check_origin_out == "" or check_origin_out is None:
            add_origin_call = self._git_call('remote', 'add', 'origin', self._remote_uri)
            if add_origin_call.returncode != 0:
                raise GitException('Unknown error occurred setting up remote')
        elif check_origin_out != self._remote_uri:
            reset_origin_call = self._git_call('remote', 'set-url', 'origin', self._remote_uri)
            if reset_origin_call.returncode != 0:
                raise GitException("Unknown error occurred resetting remote")
        self._origin_checked = True

    def _stash_changes(self):
        stash_call = self._git_call('stash', 'save', '--keep-index', '--include-untracked')
        stash_call_out = stash_call.stdout.decode('utf-8').strip()
        if stash_call.returncode != 0 and self._no_init_commit not in stash_call_out:
            raise GitException('Unknown error stashing local changes')

    def _rollback_from_stash(self):
        stash_call = self._git_call('stash', 'pop')
        if stash_call.returncode != 0:
            raise GitException("Unknown error rolling back from local stash")

    def _reset_from_origin(self):
        def _reset_error():
            raise GitException("Could not reset from origin/master. If nothing exists yet in origin, this is to be expected")
        fetch_call = self._git_call('fetch', 'origin', 'master')
        if fetch_call.returncode != 0:
            _reset_error()
        reset_call = self._git_call('reset', '--hard', 'origin/master')
        if reset_call.returncode != 0:
            _reset_error()

    def _stage_changes(self):
        stage_call = self._git_call('add', '--all')
        if stage_call.returncode != 0:
            raise GitException('Problem adding changes to staging')

    def _commit_changes(self):
        commit_message = "'Push to remote {}'".format(
            datetime.now().strftime("%m.%d.%Y-%H.%M.%S")
        )
        commit_call = self._git_call('commit', '-m', commit_message)
        if commit_call.returncode != 0:
            raise GitException('Could not commit staged changes.')

    def _push_changes(self, force=False):
        push_args = ['push', 'origin', '-u', 'master']
        if force == True:
            push_args.append('--force')
        push_args = tuple(push_args)
        push_call = self._git_call(*push_args)
        if push_call.returncode != 0:
            raise GitException('Could not push committed changes')

    def _git_call(self, *args):
        call_args = ['git']
        call_args.extend(args)
        return subprocess.run(
            call_args,
            cwd=str(self._local_backend_path),
            capture_output=True
        )


class GitException(Exception):
    pass