# Setup VM to run

For high concurrency testing, it is useful to run Locust on a VM where you can easily add more resources for bigger tests. Here is a script
for setting up a new VM to run Locust.

If your own machine is sufficient, jump to the [Running Locally](#running-locally) section.

```
apt-get update -y
apt-get upgrade -y
apt-get install -y docker.io git tmux htop sysstat iftop tcpdump
curl -SL https://github.com/docker/compose/releases/download/v2.7.0/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
chmod a+x /usr/local/bin/docker-compose

cat << EOF > /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {"max-size": "10m", "max-file": "3"}
}
EOF

# Add swap file to add reliability to memory management...
dd if=/dev/zero of=/swap bs=1M count=512
chmod 0600 /swap
mkswap /swap
cat << EOF >> /etc/fstab
# add
/swap swap      swap    defaults        0 2
EOF

reboot
```