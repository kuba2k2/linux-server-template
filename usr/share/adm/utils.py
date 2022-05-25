#!/usr/bin/python3

import os
from glob import glob
import string, random


def get_directive(username, domain, custom_root, proxy_port, proxy_host):
    if custom_root:
        return f'Use VHostDir {domain} {username} {custom_root}'
    elif proxy_host:
        return f'Use VHostProxyHost {domain} {username} {proxy_host} {proxy_port}'
    elif proxy_port:
        return f'Use VHostProxy {domain} {username} {proxy_port}'
    else:
        return f'Use VHost {domain} {username}'


def get_domain_id(username, domain):
    usernum = int(os.popen('id -u ' + username).read()) % 1000 + 1
    files = glob(f'/etc/apache2/sites-available/{usernum}*-*.conf')
    maxdomain = list(int(file.partition('available/'+str(usernum))[2].partition('-')[0]) for file in files)
    if len(maxdomain) > 0:
        maxdomain = max(maxdomain)
    else:
        maxdomain = 0
    domainnum = usernum * 100 + maxdomain+1

    for file in files:
        if '-'+domain+'.conf' in file:
            domainnum = int(file.partition('available/')[2].partition('-')[0])
            print('Reusing existing domain!')
    return f'{domainnum}-{domain}'


def get_domain_top(domain): 
    domain = domain.rpartition('.')
    domain = domain[0].rpartition('.')[2] + domain[1] + domain[2]
    return domain

def is_domain_top(domain):
    return domain == get_domain_top(domain)

def get_uid(username):
    return int(os.popen('id -u ' + username).read())
def get_gid(username):
    return int(os.popen('id -g ' + username).read())

def random_password(length):
    letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters) for i in range(length))
