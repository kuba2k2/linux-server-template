#!/usr/bin/python3

import os
from utils import get_domain_id, get_domain_top, get_uid, get_gid, random_password
import sqlite3, crypt


def configure(username, domain, ssl=False):
    domain = get_domain_top(domain) 

    if ssl:
        print('Requesting Let\'s Encrypt certificate for E-Mail...')
        os.system(f'certbot certonly --apache --keep -d mail.{domain} -d autoconfig.{domain} -d autodiscover.{domain} -d imap.{domain} -d pop3.{domain} -d smtp.{domain}')
    
        cert = f'/etc/letsencrypt/live/mail.{domain}/fullchain.pem'
        key = f'/etc/letsencrypt/live/mail.{domain}/privkey.pem'

    print('Saving Apache Mail config...')
    os.system(f'grep {domain} /etc/apache2/sites-available/001-mail.conf || echo "Use MailConfig' + ('NoSSL' if not ssl else '') + f' {domain}" >> /etc/apache2/sites-available/001-mail.conf')

    if ssl:
        print('Saving Dovecot SSL config...')
        with open(f'/etc/dovecot/conf.d/cert-{domain}.conf', 'w') as f:
            names = ['mail.'+domain, 'pop3.'+domain, 'imap.'+domain]
            for name in names:
                f.write('local_name '+name+' {\n')
                f.write('  ssl_cert = <'+cert+'\n')
                f.write('  ssl_key = <'+key+'\n')
                f.write('}\n\n')

    print('Saving Postfix domains...')
    os.system(f'grep {domain} /etc/postfix/virtual_mailbox_domains || echo "{domain} #domain" >> /etc/postfix/virtual_mailbox_domains')
    if ssl:
        print('Saving Postfix SSL config...')
        os.system(f'grep mail.{domain} /etc/postfix/vmail_ssl.map || echo >> /etc/postfix/vmail_ssl.map')
        os.system(f'grep mail.{domain} /etc/postfix/vmail_ssl.map || echo "mail.{domain} {key} {cert}" >> /etc/postfix/vmail_ssl.map')
        os.system(f'grep smtp.{domain} /etc/postfix/vmail_ssl.map || echo "smtp.{domain} {key} {cert}" >> /etc/postfix/vmail_ssl.map')

    print('Creating mail directory')
    dir = f'/home/{username}/domains/{domain}/mail'
    os.system('mkdir -p '+dir)
    os.system(f'chown {username}:{username} '+dir)
    os.system('chmod 700 '+dir)
    
    os.system(f'mkdir -p /var/log/apache2/domains/mail.{domain}')

    print('Updating Postfix maps...')
    if ssl:
        os.system('postmap -F /etc/postfix/vmail_ssl.map')
    os.system('postmap /etc/postfix/virtual_mailbox_domains')

    print('Restarting Dovecot...')
    os.system('service dovecot restart')
    print('Restarting Postfix...')
    os.system('service postfix restart')


emails = []
def _load_all():
    conn = sqlite3.connect('/etc/dovecot/authdb.sqlite')
    c = conn.cursor()
    c.execute('SELECT * FROM users;')
    global emails
    emails = []
    for row in c.fetchall():
        row = dict(zip([c[0] for c in c.description], row))
        emails.append(row)
    conn.close()


def list_all():
    if not emails:
        _load_all()
    return emails


def create(username, domain, email, password=None):
    # domain = get_domain_top(domain)
    print(f'Creating {email}@{domain} for user {username}')
    
    if os.popen(f'grep {domain} /etc/apache2/sites-available/001-mail.conf').read().strip() == '':
        configure(username, domain)

    uid = get_uid(username)
    gid = get_gid(username)
    home = f'/home/{username}'
    if not password:
        password = random_password(12)
    password_hash = crypt.crypt(password, crypt.mksalt(crypt.METHOD_SHA256))

    global emails
    emails = []

    conn = sqlite3.connect('/etc/dovecot/authdb.sqlite')
    c = conn.cursor()
    c.execute('DELETE FROM users WHERE username = ? AND domain = ?;', (email, domain))
    c.execute('INSERT INTO users (username, domain, password, home, uid, gid) VALUES (?, ?, ?, ?, ?, ?);', (email, domain, password_hash, home, uid, gid))
    conn.commit()
    conn.close()

    print(f'\n\n\t\tNew password of {email}@{domain}: {password}')
    domain = get_domain_top(domain)
    print(f'\t\tPOP3 hostname: pop3.{domain}')
    print(f'\t\tSMTP hostname: smtp.{domain}\n\n')
    print('Restarting Dovecot...')
    os.system('service dovecot restart')


if __name__ == "__main__":
    _load_all()
    print(emails)
