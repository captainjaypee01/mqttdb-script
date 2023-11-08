import os

os.system("sudo logrotate -vf /etc/logrotate.d/rsyslog")
os.system("sudo logrotate -vf /etc/logrotate.d/fail2ban")
