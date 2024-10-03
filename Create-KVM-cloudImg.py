import os
import random
import subprocess
import getpass

# Prompt user for VM name, username, and password
VM_NAME = input("Enter the VM name: ")
USERNAME = input("Enter the username: ")
PASSWORD = getpass.getpass("Enter the password for user {}: ".format(USERNAME))

# Set other variables
MAC_ADDR = '52:54:00:{:02x}:{:02x}:{:02x}'.format(
    random.randint(0, 255),
    random.randint(0, 255),
    random.randint(0, 255)
)
INTERFACE = 'eth001'
IP_ADDR = '192.168.122.101'
UBUNTU_RELEASE = 'jammy'
VM_IMAGE = f'{UBUNTU_RELEASE}-server-cloudimg-amd64.img'

# Ensure the image file exists
if not os.path.exists(VM_IMAGE):
    print(f"Error: The image file {VM_IMAGE} does not exist.")
    exit(1)

# Create the QCOW2 image for the VM
subprocess.run([
    'qemu-img', 'create', '-F', 'qcow2', '-b', f'./{VM_IMAGE}',
    '-f', 'qcow2', f'./{VM_NAME}.qcow2', '10G'
], check=True)

# Create the VM-specific network-config file
network_config_filename = f'{VM_NAME}-network-config'
network_config = f"""ethernets:
    {INTERFACE}:
        addresses:
        - {IP_ADDR}/24
        dhcp4: false
        gateway4: 192.168.122.1
        match:
            macaddress: {MAC_ADDR}
        nameservers:
            addresses:
            - 1.1.1.1
            - 8.8.8.8
        set-name: {INTERFACE}
version: 2
"""
with open(network_config_filename, 'w') as f:
    f.write(network_config)

# Create the VM-specific user-data file
user_data_filename = f'{VM_NAME}-user-data'
user_data = f"""#cloud-config
hostname: {VM_NAME}
manage_etc_hosts: true
users:
  - name: {USERNAME}
    sudo: ALL=(ALL) NOPASSWD:ALL
    groups: users, admin
    home: /home/{USERNAME}
    shell: /bin/bash
    lock_passwd: false
ssh_pwauth: true
disable_root: false
chpasswd:
  list: |
    {USERNAME}:{PASSWORD}
  expire: false
"""
with open(user_data_filename, 'w') as f:
    f.write(user_data)

# Create the VM-specific meta-data file
meta_data_filename = f'{VM_NAME}-meta-data'
with open(meta_data_filename, 'w') as f:
    f.write('')

# Generate the seed image using cloud-localds with VM-specific files
seed_image_filename = f'{VM_NAME}-seed.qcow2'
subprocess.run([
    'cloud-localds', '-v', f'--network-config={network_config_filename}',
    seed_image_filename, user_data_filename, meta_data_filename
], check=True)

# Install the virtual machine using virt-install
virt_install_cmd = [
    'virt-install',
    '--connect', 'qemu:///system',
    '--virt-type', 'kvm',
    '--name', VM_NAME,
    '--ram', '2048',
    '--vcpus', '2',
    '--os-variant', 'ubuntu22.04',
    '--disk', f'path=./{VM_NAME}.qcow2,device=disk',
    '--disk', f'path=./{seed_image_filename},device=disk',
    '--import',
    '--network', f'network=default,model=virtio,mac={MAC_ADDR}',
    '--noautoconsole'
]
subprocess.run(virt_install_cmd, check=True)
