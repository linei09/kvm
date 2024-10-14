KVM on Ubuntu 22.04 LTS (Jammy Jellyfish) cloud images
1. Check: ``` egrep -c '(vmx|svm)' /proc/cpuinfo``` 
2. Check: ``` sudo kvm-ok``` 
3. Install:
   
   ```
   sudo apt update
   sudo apt install qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils virt-manager cloud-image-utils
   ```
5. Add yourself to the libvirt and kvm groups:

   ```
   sudo adduser $USER libvirt
   sudo adduser $USER kvm
   ``` 
7. Check: ```virsh list --all```
8. Check: ```sudo systemctl status libvirtd```
9. Export needed variables:
```
   export MAC_ADDR=$(printf '52:54:00:%02x:%02x:%02x' $((RANDOM%256)) $((RANDOM%256)) $((RANDOM%256)))
   export INTERFACE=eth001
   export IP_ADDR=192.168.122.101
   export VM_NAME=vm01
   export UBUNTU_RELEASE=jammy
   export VM_IMAGE=$UBUNTU_RELEASE-server-cloudimg-amd64.img
```
11. Download the Ubuntu 22.04 cloud image:
```
wget https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64.img
```
9. Create a disk image:
```
qemu-img create -F qcow2 -b ./$VM_IMAGE -f qcow2 ./$VM_NAME.qcow2 10G
```
11. Create cloud-init files:
```
cat >network-config <<EOF                                                             
ethernets:    
    $INTERFACE:
        addresses:
        - $IP_ADDR/24
        dhcp4: false
        gateway4: 192.168.122.1
        match:
            macaddress: $MAC_ADDR
        nameservers:
            addresses:
            - 1.1.1.1
            - 8.8.8.8
        set-name: $INTERFACE
version: 2
EOF

cat >user-data <<EOF
#cloud-config
hostname: $VM_NAME
manage_etc_hosts: true
users:
  - name: vmadm
    sudo: ALL=(ALL) NOPASSWD:ALL
    groups: users, admin
    home: /home/vmadm
    shell: /bin/bash
    lock_passwd: false
ssh_pwauth: true
disable_root: false
chpasswd:
  list: |
    vmadm:vmadm
  expire: false
EOF
```

```touch meta-data```

11. Attach cloud-init to the image:
  ``` cloud-localds -v --network-config=network-config ./$VM_NAME-seed.qcow2 user-data meta-data``` 

13. Create the VM:
```
virt-install --connect qemu:///system \
  --virt-type kvm \
  --name $VM_NAME \
  --ram 2048 \
  --vcpus 2 \
  --os-variant ubuntu22.04 \
  --disk path=$VM_IMAGE,device=disk \
  --disk path=$VM_NAME-seed.qcow2,device=disk \
  --import \
  --network network=default,model=virtio,mac=$MAC_ADDR \
  --noautoconsole

```
- Nếu muốn đổi dùng ip mặc định do kvm cấp bằng dhcp thì không cần network-config và đổi thành như thế này

  ```--network bridge=virbr0,model=virtio,mac=$MAC_ADDR```


  modify user-data
  ![image](https://github.com/user-attachments/assets/dea5f079-711a-4136-9ce2-be68021c5d19)
+ restart máy
