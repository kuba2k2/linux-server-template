#!/usr/bin/python3

import os
from glob import glob
from utils import get_domain_id, get_directive, is_domain_top
import emails


def create(username, domain, enable_80, enable_443, redirect_ssl, custom_root, proxy_port, cert_name, config_mail):
    domain_id = get_domain_id(username, domain)

    print(f'Domain ID: {domain_id}')

    if not cert_name and enable_443:
        print('Requesting Let\'s Encrypt certificate for HTTPS...')
        os.system(f'certbot certonly --apache --keep -d {domain}' + (' -d www.'+domain if is_domain_top(domain) else ''))
    
    print('Writing Apache config...')
    with open(f'/etc/apache2/sites-available/{domain_id}.conf', 'w') as f:
        if enable_80:
            f.write('<VirtualHost *:80>\n')
            if redirect_ssl:
                f.write(f'\tUse VHostToSSL {domain}\n')
            else:
                f.write('\t'+get_directive(username, domain, custom_root, proxy_port)+'\n')
            f.write('</VirtualHost>\n\n')

        if enable_443:
            f.write('<VirtualHost *:443>\n')
            f.write('\t'+get_directive(username, domain, custom_root, proxy_port)+'\n')
            if cert_name:
                f.write(f'\tUse LetsEncrypt {cert_name}\n')
            else:
                f.write(f'\tUse LetsEncrypt {domain}\n')
            f.write('</VirtualHost>\n\n')

        f.write('# vim: syntax=apache ts=4 sw=4 sts=4 sr noet')

    print('Creating domain directories...')
    os.system(f'mkdir -p /home/{username}/domains/{domain}/public_html')
    dirs = [
        f'/home/{username}/domains',
        f'/home/{username}/domains/{domain}',
        f'/home/{username}/domains/{domain}/public_html',
        f'/home/{username}/domains/{domain}/stats'
    ]
    for dir in dirs:
        os.system('mkdir -p '+dir)
        os.system(f'chown {username}:{username} '+dir)
        os.system('chmod 700 '+dir)

    print('Creating log directories...')
    os.system(f'mkdir -p /var/log/apache2/domains/{domain}')

    print('Writing Webalizer config...')
    with open(f'/etc/webalizer/{domain_id}.conf', 'w') as f:
        f.write(f'LogFile /var/log/apache2/domains/{domain}/access.log.1\n')
        f.write(f'OutputDir /home/{username}/domains/{domain}/stats\n')
        f.write(f'HostName {domain}\n')

    if config_mail:
        emails.configure(username, domain, enable_443)
    os.system(f'a2ensite {domain_id}')
    print('Restarting Apache...')
    os.system('service apache2 restart')


def delete(username, remove_files=False):
    if remove_files:
        os.system(f'deluser --remove-home {username}')
    else:
        os.system(f'deluser {username}')


vhosts = []
mail_config = []
def _load_all():
    global vhosts, mail_config
    for site in glob('/etc/apache2/sites-available/*.conf'):
        with open(site) as f:
            conf = f.read().split("\n")
            in_vhost = False
            vhost = {'name': None}
            for line in conf:
                if line.startswith('#'):
                    continue
                if line.startswith('<VirtualHost'):
                    in_vhost = True
                    vhost['port'] = line.rpartition(':')[2].partition('>')[0]
                elif line.startswith('</VirtualHost'):
                    in_vhost = False
                    vhosts.append(vhost)
                    vhost = {'name': None}
                elif line.startswith('Use MailConfig'):
                    mail_config.append(line.rpartition(' ')[2])
                elif in_vhost:
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith('ServerName'):
                        vhost['name'] = line.partition(' ')[2]
                    elif line.startswith('ServerAlias'):
                        if not 'aliases' in vhost:
                            vhost['aliases'] = []
                        vhost['aliases'].append(line.split(' ')[1:])
                    elif line.startswith('ServerAdmin'):
                        vhost['admin'] = line.partition(' ')[2]
                    elif line.startswith('Use VHostToSSL'):
                        vhost['name'] = line.rpartition(' ')[2]
                        vhost['is_to_ssl'] = True
                        in_vhost = False
                    elif line.startswith('Use VHostDir'):
                        line = line.split(' ')[2:]
                        vhost['name'] = line[0]
                        vhost['username'] = line[1]
                        vhost['custom_dir'] = line[2]
                    elif line.startswith('Use VHostProxy'):
                        line = line.split(' ')[2:]
                        vhost['name'] = line[0]
                        vhost['username'] = line[1]
                        vhost['proxy_port'] = line[2]
                    elif line.startswith('Use VHost '):
                        line = line.split(' ')[2:]
                        vhost['name'] = line[0]
                        vhost['username'] = line[1]
                    elif line.startswith('Use LetsEncrypt'):
                        vhost['cert_name'] = line.rpartition(' ')[2]
                    else:
                        # print(line)
                        pass

    domains = set(map(lambda vhost: vhost['name'], vhosts))
    vhosts = {domain: [vhost for vhost in vhosts if vhost['name'] == domain] for domain in domains}


def list_all(username=None):
    if not vhosts:
        _load_all()
    return set([vhost['name'] for vhosts in vhosts.values() for vhost in vhosts if not username or 'username' in vhost and vhost['username'] == username])


def get(domain):
    if not vhosts:
        _load_all()
    if domain in vhosts:
        return vhosts[domain]
    return None

def get_user(domain_obj):
    if not domain_obj:
        return None
    for vhost in domain_obj:
        if 'username' in vhost:
            return vhost['username']
    return None

