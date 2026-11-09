#!/usr/bin/env bash
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y ca-certificates curl gnupg nginx certbot python3-certbot-nginx
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
. /etc/os-release
printf 'deb [arch=%s signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu %s stable\n' "$(dpkg --print-architecture)" "$VERSION_CODENAME" > /etc/apt/sources.list.d/docker.list
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable --now docker nginx
if ! swapon --show=NAME --noheadings | grep -q .; then
    fallocate -l 2G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    printf '/swapfile none swap sw 0 0\n' >> /etc/fstab
fi
printf 'vm.swappiness=10\n' > /etc/sysctl.d/99-moveinmate.conf
sysctl --system > /dev/null
install -d -m 0750 -o ubuntu -g ubuntu /opt/moveinmate
install -d -m 0700 -o ubuntu -g ubuntu /opt/moveinmate-backups
printf 'PasswordAuthentication no\nPermitRootLogin no\n' > /etc/ssh/sshd_config.d/00-moveinmate.conf
install -d -m 0755 /run/sshd
sshd -t
systemctl reload ssh
install -m 0644 /dev/null /var/lib/moveinmate-bootstrap-ready
