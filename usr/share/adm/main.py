#!/usr/bin/python3

import os, sys
import users, domains, emails


def create_delete(what):
    inp = input(f'[C]reate, [D]elete {what}? ')[:1].lower()
    return 'd' if inp == 'd' else 'c' if inp == 'c' else 'a'

def create_update_delete(what):
    inp = input(f'[C]reate, [U]pdate, [D]elete {what}? ')[:1].lower()
    return 'd' if inp == 'd' else 'c' if inp == 'c' else 'u' if inp == 'u' else 'a'


def enter_user():
    return input('Enter a username: ')

def choose_user():
    userlist = users.list_all()
    print('Choose a user:')
    index = 0
    for username, user in userlist.items():
        print(f' - {index}: {username} - {user["gecos"][0]}')
        index += 1
    index = int(input())
    username = list(userlist)[index]
    return username


def enter_domain():
    return input('Enter a domain name: ')

def choose_domain(username, list_only=False):
    domainlist = domains.list_all(username)
    if not list_only:
        print('Choose a domain:')
    index = 0
    for domain in domainlist:
        print(f' - {index}: {domain}')
        index += 1
    if list_only:
        return
    index = int(input())
    domain = list(domainlist)[index]
    return domain


def enter_email():
    email = input('Enter an email address: ').partition('@')
    return email[0], email[2]

def choose_email():
    emaillist = emails.list_all()
    index = 0
    for email in emaillist:
        print(f' - {index}: {email["username"]}@{email["domain"]}, user {email["home"].rpartition("/")[2]}')
        index += 1
    index = int(input())
    email = emaillist[index]
    return email


def manage_users():
    cd = create_delete('user')
    if cd == 'c':
        username = enter_user()
        users.create(username)
        return f'Created user {username}'
    elif cd == 'd':
        username = choose_user()
        remove_files = True if input(f'Remove ALL files of user "{username}"? [YES], [n]o') == 'YES' else False
        users.delete(username, remove_files)
        return f'Deleted user {username}'


def manage_domains():
    username = choose_user()
    print(f'Domains of user {username}:')
    choose_domain(username, list_only=True)
    print()
    cd = create_update_delete('domain')
    if cd == 'c' or cd == 'u':
        if cd == 'c':
            domain = enter_domain()
        else:
            domain = choose_domain(username)
        print(' - Do [n]ot enable SSL')
        print(' - [E]nable SSL, do not redirect from HTTP')
        print(' * Enable SSL, [r]edirect HTTP to HTTPS')
        print(' - Enable [o]nly SSL')
        ssl = input()[:1].lower()
        ssl = 'n' if ssl == 'n' else 'e' if ssl == 'e' else 'o' if ssl == 'o' else 'r'
        print('VirtualHost type')
        print(' * [N]ormal, public_html in user\'s homedir')
        print(' - [C]ustom document root')
        print(' - [P]roxy to a TCP port')
        vht = input()[:1].lower()
        vht = 'c' if vht == 'c' else 'p' if vht == 'p' else 'n'
        if vht == 'c':
            custom_root = input('   Enter path to document root: ')
        elif vht == 'p':
            proxy_port = int(input('    Enter the reverse proxy port: '))
        if ssl != 'n':
            cert = input('Existing certificate name, [s] to use server certificate, or empty to obtain new for domain:\n    ')
            if cert == 's':
                print('    Using server certificate (server.hostname)')
        mail = input('Configure e-mail? (cert + SMTP/POP3/IMAP VHost) [y]es, *[n]o ')[:1].lower() == 'y'
        domains.create(
                username,
                domain, 
                enable_80=ssl != 'o', enable_443=ssl != 'n', redirect_ssl=ssl == 'r',
                custom_root=custom_root if vht == 'c' else None,
                proxy_port=proxy_port if vht == 'p' else None,
                cert_name=None if ssl == 'n' else 'vps.szkolny.eu' if cert == 's' else cert,
                config_mail=mail
        )
        return f'Created domain {domain} for user {username}'


def manage_emails():
    cd = create_update_delete('e-mail')
    if cd == 'c':
        email, domain = enter_email()
        username = domains.get_user(domains.get(domain))
        emails.create(username, domain, email)
    elif cd == 'u':
        email = choose_email()
        username = email["home"].rpartition('/')[2]
        password = input('Enter new password: ')
        emails.create(username, email['domain'], email['username'], password)
    elif cd == 'd':
        pass


def dns_config():
    domain = enter_domain()
    mail = 'mail.'+domain
    ip = '192.168.0.1'
    print(f'A\t{domain}\t\t{ip}')
    print(f'A\tmail\t\t\t{ip}')
    print(f'CNAME\tautoconfig\t\t{mail}')
    print(f'CNAME\tautodiscover\t\t{mail}')
    print(f'CNAME\timap\t\t\t{mail}')
    print(f'CNAME\tpop3\t\t\t{mail}')
    print(f'CNAME\tsmtp\t\t\t{mail}')
    print(f'CNAME\twww\t\t\t{domain}')
    print(f'MX\t{domain}\t\t{mail}')
    print(f'SRV\t_autodiscover._tcp\t10 10 443 autodiscover.{domain}')
    print(f'SRV\t_imaps._tcp\t\t10 10 993 imap.{domain}')
    print(f'SRV\t_pop3s._tcp\t\t10 10 995 pop3.{domain}')
    print(f'SRV\t_submission._tcp\t10 10 465 smtp.{domain}')
    print(f'TXT\t{domain}\t\tv=spf1 mx ip4:192.168.0.1 ~all')
    print('\n\n')
    print(f'{domain}.\t1\tIN\tA\t{ip}')
    print(f'mail.{domain}.\t1\tIN\tA\t{ip}')
    print(f'autoconfig.{domain}.\t1\tIN\tCNAME\t{mail}.')
    print(f'autodiscover.{domain}.\t1\tIN\tCNAME\t{mail}.')
    print(f'imap.{domain}.\t1\tIN\tCNAME\t{mail}.')
    print(f'pop3.{domain}.\t1\tIN\tCNAME\t{mail}.')
    print(f'smtp.{domain}.\t1\tIN\tCNAME\t{mail}.')
    print(f'www.{domain}.\t1\tIN\tCNAME\t{domain}.')
    print(f'{domain}.\t1\tIN\tMX\t10 {mail}.')
    print(f'_autodiscover._tcp.{domain}.\t1\tIN\tSRV\t10 10 443 autodiscover.{domain}.')
    print(f'_imaps._tcp.{domain}.\t1\tIN\tSRV\t10 10 993 imap.{domain}.')
    print(f'_pop3s._tcp.{domain}.\t1\tIN\tSRV\t10 10 995 pop3.{domain}.')
    print(f'_submission._tcp.{domain}.\t1\tIN\tSRV\t10 10 465 smtp.{domain}.')
    print(f'{domain}.\t1\tIN\tTXT\t"v=spf1 mx ip4:192.168.0.1 ~all"')
    return ''

if __name__ == "__main__":
    print(' - Manage [u]sers')
    print(' - Manage [d]omains')
    print(' - Manage e-[m]ails')
    print(' - Manage virtual [F]TP')
    print(' - Print suggested D[N]S config')
    a = input('Choose an action: ')[0].lower()
    actions = {
        'u': manage_users,
        'd': manage_domains,
        'm': manage_emails,
        'n': dns_config
    }
    func = actions.get(a, lambda: 'Invalid action')
    print(func())
