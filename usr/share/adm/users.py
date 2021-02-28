#!/usr/bin/python3

import os

def create(username):
    os.system(f'adduser --disabled-password {username}')
    os.makedirs(f'/home/{username}/domains')
    os.makedirs(f'/home/{username}/mail')


def delete(username, remove_files=False):
    if remove_files:
        os.system(f'deluser --remove-home {username}')
    else:
        os.system(f'deluser {username}')


def list_all():
    with open('/etc/passwd') as f:
        users = f.read()
        users = (c.split(':') for c in users.split("\n"))
        users = {a[0]: {
            'uid': int(a[2]),
            'gid': int(a[3]),
            'gecos': a[4].split(','),
            'home': a[5]
        } for a in users if len(a) > 1 and a[5].startswith('/home/') and os.path.isdir(a[5])}
        return users


if __name__ == "__main__":
    get_users()
