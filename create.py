import libvirt
import os
import shutil

# Kết nối tới hypervisor KVM
conn = libvirt.open('qemu:///system')
if conn is None:
    print('Failed to open connection to qemu:///system')
    exit(1)

# Đường dẫn tới file QCOW2 gốc
qcow2_path = "/home/ubutnu/Desktop/ubuntu22.04.qcow2"

# Kiểm tra xem file QCOW2 có tồn tại không
if not os.path.exists(qcow2_path):
    print(f"File {qcow2_path} does not exist")
    conn.close()
    exit(1)

# Nhập tên máy ảo từ người dùng
vm_name = input("Enter the name for the virtual machine: ").strip()

# Kiểm tra nếu tên máy ảo không rỗng và không chứa ký tự không hợp lệ
if not vm_name or any(char in vm_name for char in '/\\:*?"<>|'):
    print("Invalid virtual machine name.")
    conn.close()
    exit(1)

# Tạo đường dẫn cho bản sao QCOW2
new_qcow2_path = f"/var/lib/libvirt/images/{vm_name}.qcow2"

# Sao chép file QCOW2 gốc
try:
    shutil.copyfile(qcow2_path, new_qcow2_path)
except Exception as e:
    print(f"Failed to copy QCOW2 file: {e}")
    conn.close()
    exit(1)

# Định nghĩa XML cho máy ảo với 5 PCIe controllers và hỗ trợ hotplugging
pci_controllers = "<controller type='pci' index='0' model='pcie-root'/>"  # Root PCIe controller
for i in range(1, 6):  # 5 PCI controllers
    pci_controllers += f"<controller type='pci' index='{i}' model='pcie-root-port'/>"

# Định nghĩa XML cho máy ảo với 5 PCI controllers
domain_xml = f"""
<domain type='kvm'>
  <name>{vm_name}</name>
  <memory unit='KiB'>4194304</memory> <!-- RAM 4GB -->
  <vcpu placement='static'>4</vcpu> <!-- 2 CPUs -->
  <cpu mode='host-passthrough'>
    <feature policy='require' name='vmx'/>
  </cpu>
  <os>
    <type arch='x86_64' machine='pc-q35-6.1'>hvm</type>
    <boot dev='hd'/>
    <acpi/>
  </os>
  <devices>
    <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2'/>
      <source file='{new_qcow2_path}'/>
      <target dev='vda' bus='virtio'/>
    </disk>
    <interface type='network'>
      <source network='default'/>
    </interface>
    {pci_controllers} <!-- 5 PCI Controllers -->
    <video>
      <model type='qxl'/>
    </video>
    <console type='pty'>
      <target type='serial' port='0'/>
    </console>
    <graphics type='spice' autoport='yes' listen='0.0.0.0'>
      <listen type='address' address='0.0.0.0'/>
    </graphics>
  </devices>
</domain>
"""

# Định nghĩa và khởi động máy ảo với cấu hình hỗ trợ hotplugging
try:
    domain = conn.defineXML(domain_xml)
    if domain is None:
        print(f"Failed to define the domain {vm_name}.")
    else:
        domain.create()
        print(f"Virtual Machine '{vm_name}' has been defined and started successfully with hotplugging support.")
except libvirt.libvirtError as e:
    print(f"Failed to create and start the domain: {e}")

# Đóng kết nối
conn.close()
