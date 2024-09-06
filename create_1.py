import libvirt
import os
import shutil

# Kết nối tới hypervisor KVM
conn = libvirt.open('qemu:///system')
if conn is None:
    print('Failed to open connection to qemu:///system')
    exit(1)

# Đường dẫn tới file QCOW2 gốc
qcow2_path = "/home/ubuntu/Desktop/ubuntu22.04.qcow2"

# Kiểm tra xem file QCOW2 có tồn tại không
if not os.path.exists(qcow2_path):
    print(f"File {qcow2_path} does not exist")
    exit(1)

# Nhập tên máy ảo từ người dùng
vm_name = input("Enter the name for the virtual machine: ").strip()

# Kiểm tra nếu tên máy ảo không rỗng và không chứa ký tự không hợp lệ
if not vm_name or any(char in vm_name for char in '/\\:*?"<>|'):
    print("Invalid virtual machine name.")
    exit(1)

# Tạo đường dẫn cho bản sao QCOW2
new_qcow2_path = f"/var/lib/libvirt/images/{vm_name}.qcow2"

# Sao chép file QCOW2 gốc
shutil.copyfile(qcow2_path, new_qcow2_path)

# Định nghĩa XML cho máy ảo với bản sao QCOW2
domain_xml = f"""
<domain type='kvm'>
  <name>{vm_name}</name>
  <memory unit='KiB'>2097152</memory> <!-- RAM 2GB -->
  <vcpu placement='static'>2</vcpu> <!-- 2 CPUs -->
  <os>
    <type arch='x86_64' machine='pc'>hvm</type>
    <boot dev='hd'/>
  </os>
  <devices>
    <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2'/>
      <source file='{new_qcow2_path}'/>
      <target dev='vda' bus='virtio'/>
    </disk>
    <interface type='network'>
      <mac address='52:54:00:6b:3c:58'/>
      <source network='default'/>
      <model type='virtio'/>
    </interface>
    <console type='pty'>
      <target type='serial' port='0'/>
    </console>
    <graphics type='vnc' port='-1' autoport='yes'/>
  </devices>
</domain>
"""

# Tạo máy ảo từ XML
try:
    domain = conn.createXML(domain_xml, 0)
    print(f"Virtual Machine '{vm_name}' has been created and started successfully.")
except libvirt.libvirtError as e:
    print(f"Failed to create a domain: {e}")

# Đóng kết nối
conn.close()
