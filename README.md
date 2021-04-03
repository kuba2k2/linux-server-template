# linux-server-template

A simple, kinda-ready-to-use template for easy administration of a basic Linux webserver.

It worked on two servers so far, so that's already something.

## How to install

Provided you already have apache installed, you need some additional modules.

```bash
# apt install libapache2-mpm-itk libapache2-mod-authnz-external pwauth libapache2-mod-remoteip
# a2enmod authnz_external
# a2enmod mpm_itk
# a2enmod macro
# a2enmod remoteip
```

You should also have webalizer (for website stats) and certbot (Let's Encrypt SSL certificates).
```bash
# apt install webalizer certbot python3-certbot-apache
# a2enmod ssl
```

Then just copy the directory structure from this repository to replace the configuration files.

Replace `server.hostname` with your main server hostname and `192.168.0.1` with your server IP in:
- `/usr/share/adm/main.py`
- `/etc/webalizer/webalizer.conf`

Edit `/etc/apache2/conf-available/vhost-macro.conf` and replace `$user ubuntu admin` with a list of
users allowed to see website stats (`$user` means the domain owner account).

Enable apache2 configuration files.
```bash
# a2enconf vhost-macro
# a2enconf mail-autoconfig
# a2enconf remoteip
```

## Congratulations

After completing these steps there is a chance that this configuration will work.

