#!/bin/bash

# Overview: This script provides a comprehensive one-shot overview of the host system.
# It captures various system information including OS details, kernel version, uptime,
# load average, storage, partition, CPU and memory info, network details, locale, 
# user information, package details, security updates, top processes, Docker information, 
# and running services.

# Function to check and install missing commands
ensure_command() {
    if ! command -v "$1" &> /dev/null; then
        echo "Command $1 not found, installing..."
        apt-get update && apt-get install -y "$1"
    fi
}

# Ensure necessary commands are available
commands=(lsb_release df lsblk nproc awk ifconfig ip grep hostname dnsdomainname localectl timedatectl whoami id dpkg ps uname uptime free service apt)
for cmd in "${commands[@]}"; do
    ensure_command "$cmd"
done

# Capture system information

# Debian Version
debian_version=$(lsb_release -d | awk -F"\t" '{print $2}' 2>/dev/null)

# Kernel Version
kernel_version=$(uname -r)

# Uptime
uptime=$(uptime -p)

# Load Average
load_average=$(uptime | awk -F'load average: ' '{print $2}')

# Storage Information
storage=$(df -h --total | awk '/total/ {print $2}')
storage_summary=$(df -h | awk 'NR==1; /\/$/')

# Partition Information
partition=$(lsblk -o NAME,SIZE,FSTYPE | grep -vE "loop|NAME")

# CPU Information
vcpu=$(nproc)
cpu_model=$(awk -F: '/model name/ {name=$2} END {print name}' /proc/cpuinfo)

# Memory Information
max_mem=$(awk '/MemTotal/ {print $2 / 1024 " MB"}' /proc/meminfo)
min_mem=$(awk '/MemAvailable/ {print $2 / 1024 " MB"}' /proc/meminfo)
installed_ram=$(free -m | awk '/Mem:/ {print $2 " MB"}')

# Network Information
ip=$(hostname -I | awk '{print $1}')
netmask=$(ifconfig | awk '/inet / && !/127.0.0.1/ {print $4}' | uniq)
gateway=$(ip route | awk '/default/ {print $3}')
nameserver=$(awk '/^nameserver/ {print $2}' /etc/resolv.conf | uniq)

# Hostname
hostname=$(hostname)

# Domain Information
domain=$(dnsdomainname)

# Locale and Keymap
locale=$(localectl status | awk '/System Locale/ {print $3}')
keymap=$(localectl status | awk '/VC Keymap/ {print $3}')

# Timezone
timezone=$(timedatectl | awk '/Time zone/ {print $3}')

# User Information
username=$(whoami)
user_role=$(id -Gn "$username" | tr ' ' ',')

# Number of Installed Packages
installed_packages=$(dpkg --get-selections | wc -l)

# Security Updates
security_updates=$(apt list --upgradeable 2>/dev/null | grep -i security | wc -l)

# Template ID (assuming it is stored somewhere in the system)
template_id=$(cat /etc/template_id 2>/dev/null)

# Main Usage Information
top_cpu=$(ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%cpu | head -n 6)
top_mem=$(ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%mem | head -n 6)

# Docker Information (only if Docker is installed)
if command -v docker &> /dev/null; then
    docker_version=$(docker --version 2>/dev/null)
    docker_ps=$(docker ps --format "table {{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null)
else
    docker_version="Docker not installed"
    docker_ps="N/A"
fi

# Running Services
running_services=$(service --status-all 2>&1 | grep '\[ + \]')

# Generate Timestamp
timestamp=$(date +"%Y-%m-%d %H:%M:%S")

# Output captured information using the template
cat <<EOF
# VM Description - $hostname

*Generated on: $timestamp*

## Machine Information
- **Debian Version**: $debian_version
- **Kernel Version**: $kernel_version
- **Uptime**: $uptime
- **Load Average**: $load_average
- **Storage**: $storage

### Storage Summary
\`\`\`
Filesystem                Size  Used Avail Use% Mounted on
$storage_summary
\`\`\`

### Partition
\`\`\`
$partition
\`\`\`

- **vCPU**: $vcpu
- **CPU Model**: $cpu_model
- **Max Mem**: $max_mem
- **Min Mem**: $min_mem
- **Installed RAM**: $installed_ram
- **IP**: $ip
- **Netmask**: $netmask
- **Gateway**: $gateway
- **Nameserver**: $nameserver
- **Hostname**: $hostname
- **Domain**: $domain
- **Locale**: $locale
- **Keymap**: $keymap
- **Timezone**: $timezone
- **Username**: $username
- **User Role**: $user_role
- **Installed Packages**: $installed_packages
- **Security Updates**: $security_updates
- **Template ID**: $template_id

## Top Processes by CPU Usage
\`\`\`
$top_cpu
\`\`\`

## Top Processes by Memory Usage
\`\`\`
$top_mem
\`\`\`

## Docker Information
- **Docker Version**: $docker_version

### Running Containers
\`\`\`
CONTAINER ID   IMAGE                              STATUS                    PORTS
$docker_ps
\`\`\`

## Running Services
EOF

echo "$running_services" | while read -r line; do
    echo "- [ + ]  ${line:8}"
done

echo ""
echo "## Source of Information"
echo "\`\`\`shell"
echo "/srv/script/discover.sh"
echo "\`\`\`"
