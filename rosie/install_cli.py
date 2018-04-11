from __future__ import print_function
import os, errno

default_dir = '/usr/local/bin'

def link(dir=None):
    dir = dir or default_dir
    install_dir = os.path.dirname(os.path.abspath(__file__))
    cli = os.path.join(install_dir, 'rosie_cli')
    print('Attempting to create link to', cli)
    installed_link = os.path.join(dir, 'rosie')
    try:
        os.symlink(cli, installed_link)
    except OSError as e:
        if e.errno == 17:
            print(installed_link, 'already exists -- cannot create symlink')
        else:
            raise e
        return
    print('Successfully created', installed_link)
