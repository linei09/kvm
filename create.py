import libvirt
import os
import subprocess
import random
import string

def generate_mac():
    mac = [ 0x52, 0x54, 0x00,
            random.randint(0x00, 0x7f),
            random.randint(0x00, 0xff),
            random.randint(0x00, 0xff) ]
    return ':'.join(map(lambda x: "%02x" % x, mac))

def create_vm(vm_name, image_path="/home/ubuntu/Desktop/images/abc.qcow2", network_name="default"):
    # Tạo đường dẫn mới cho tệp hình ảnh của máy ảo
    new_image_path = f"/var/lib/libvirt/images/{vm_name}.qcow2"
    
    print(f"Copying image from {image_path} to {new_image_path}")  # In ra đường dẫn trước khi sao chép
    
    # Kiểm tra xem tệp hình ảnh mới đã tồn tại chưa
    if os.path.exists(new_image_path):
        print(f"Image file {new_image_path} already exists.")
        return False

    # Kiểm tra xem tệp hình ảnh nguồn có tồn tại không
    if not os.path.exists(image_path):
        print(f"Source image file {image_path} does not exist.")
        return False

    try:
        # Sao chép tệp qcow2
        cp_process = subprocess.run(['sudo', 'cp', image_path, new_image_path], capture_output=True, text=True)
        if cp_process.returncode == 0:
            print(f"Successfully copied {image_path} to {new_image_path}")  # Thêm thông báo in ra console
        else:
            print(f"Failed to copy {image_path} to {new_image_path}: {cp_process.stderr}")
            return False
    except Exception as e:
        print(f"Failed to copy {image_path} to {new_image_path}: {e}")
        return False

    conn = libvirt.open('qemu:///system')
    if conn is None:
        print('Failed to open connection to qemu:///system')
        return False

    xml = f'''
        <domain type='kvm'>
            <name>{vm_name}</name>
            <memory unit='KiB'>4194304</memory>
            <vcpu placement='static'>2</vcpu>
            <os>
                <type arch='x86_64' machine='pc-i440fx-2.11'>hvm</type>
                <boot dev='hd'/>
            </os>
            <devices>
                <disk type='file' device='disk'>
                    <driver name='qemu' type='qcow2'/>
                    <source file='{new_image_path}'/>
                    <target dev='vda' bus='virtio'/>
                    <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x0'/>
                </disk>
                <interface type='network'>
                    <mac address='{generate_mac()}'/>
                    <source network='{network_name}'/>
                    <model type='virtio'/>
                    <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
                </interface>
                <graphics type='vnc' port='-1' autoport='yes'/>
            </devices>
        </domain>
    '''

    try:
        dom = conn.createXML(xml, 0)
        print(f"Virtual machine '{vm_name}' created successfully.")
        return True
    except Exception as e:
        print(f"Failed to create virtual machine '{vm_name}': {str(e)}")
        return False
    finally:
        conn.close()

def get_network_ip(network_name):
    try:
        output = subprocess.check_output(['virsh', 'net-dhcp-leases', network_name]).decode()
        ip_list = [line.split()[4] for line in output.split('\n')[2:] if line]
        return ip_list[0] if ip_list else None
    except Exception as e:
        print(f"Failed to get IP address from network '{network_name}': {str(e)}")
        return None

if __name__ == "__main__":
    vm_name = input("Enter VM name: ")

    if create_vm(vm_name):
        ip_address = get_network_ip("default")
        if ip_address:
           # print(f"IP address assigned to VM: {ip_address}")
        else:
           # print("Failed to retrieve IP address.")
