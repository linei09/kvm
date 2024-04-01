import libvirt
import subprocess
import os
import struct
import random
#check ovs đã đc cài chưa
ip_address_str = input("Nhập địa chỉ IP tĩnh cho interface  (ví dụ: 192.168.1.10): ")
def check_install_ovs(): 
 try:
  subprocess.check_output(['dpkg', '-l', 'openvswitch-switch'])
  print("Open vSwitch đã được cài đặt.")
  return True
 except subprocess.CalledProcessError:
  print("ovs chua duoc cai dat")
  return False
#cài ovs
def install_ovs():
 if not check_install_ovs():
  subprocess.run(['sudo','apt','update'])
  install_cmd = ['sudo','apt-get','install','-y','openvswitch-switch']
  subprocess.run(install_cmd)
 else:
  print("da duoc cai")

def create_ovs_bridge(bridge_name):
 # Kiểm tra xem ovs-vsctl có tồn tại trên hệ thống hay không
 if not os.path.exists('/usr/bin/ovs-vsctl'):
  print("ovs-vsctl không tồn tại trên hệ thống của bạn. Đang thực hiện cài đặt...")
  install_ovs()

# Tạo lệnh để tạo cầu OVS mới với tên là tên của bridge
 ovs_create_cmd = ["sudo", "ovs-vsctl", "add-br", bridge_name]

    # Thực thi lệnh để tạo cầu OVS mới
 try:
  subprocess.run(ovs_create_cmd, check=True)
  print(f"Đã tạo bridge OVS mới có tên '{bridge_name}'.")

  # Nhập địa chỉ IP từ người dùng
  ip_address = input("Nhập địa chỉ IP cho bridge: ")

  # Nhập subnet mask từ người dùng
  net_mask = input("Nhập subnet mask cho bridge: ")

  subprocess.run(["sudo", "ip", "addr", "add", f"{ip_address}/{net_mask}", "dev", bridge_name], check=True)
  subprocess.run(["sudo", "ip", "link", "set", bridge_name, "up"], check=True)

 except subprocess.CalledProcessError as e:
  print(f"Lỗi: {e}")
  print(f"Đã xảy ra lỗi khi tạo cầu OVS '{bridge_name}'.")


	
def generate_random_mac():
# Tạo một địa chỉ MAC ngẫu nhiên
 mac = [0x52, 0x54, 0x00, random.randint(0x00, 0x7f), random.randint(0x00, 0xff), random.randint(0x00, 0xff)]
 return ':'.join(map(lambda x: "%02x" % x, mac))

used_pci_slots = []
def generate_pci_slot():
 while True:
  new_slot = hex(random.randint(0, 31))  # Tạo một slot mới từ 0x00 đến 0x31 (tương đương với 0-49 ở dạng số nguyên)
  new_slot = '0x' + new_slot[2:].zfill(2)  # Đảm bảo rằng slot có đủ 2 chữ số hex và có tiền tố '0x'
  if new_slot not in used_pci_slots:
   used_pci_slots.append(new_slot)  # Thêm slot mới vào danh sách đã sử dụng
   return new_slot

for _ in range(10):
 print(generate_pci_slot())

#def generate_pci_slot():
# Generate a random slot number between 0 and 31 (0x00 to 0x1F)
 #while True:
 # slot = f"{random.randint(0, 31):02x}"
  # Check if the slot is already used
 # if slot not in used_pci_slots:
 #  used_pci_slots.append(slot)
 # return f"0000:{slot}:00.0"




def add_interface_to_vm(vm_name, bridge_name, ip_address_str,xml_config=None):
# Kiểm tra xem card mạng đã tồn tại trên hệ thống hay không


 # Mở kết nối tới libvirt
 conn = libvirt.open('qemu:///system')
 if conn is None:
  print("Không thể kết nối đến libvirt.")
  return False

 # Tìm máy ảo cần thêm card mạng
 vm = conn.lookupByName(vm_name)
 if vm is None:
  print(f"Không tìm thấy máy ảo với tên '{vm_name}'.")
  return False
 #if not check_interface_exist(interface_name):
 # print(f"Card mạng '{interface_name}' không tồn tại trên hệ thống.")
 # print(f"Đang tạo card mạng '{interface_name}'...")
 create_ovs_bridge(bridge_name)

 #ip_address = ip_to_int(ip_address_str)
# <source bridge='{bridge_name}'/>
 # Lấy cấu hình XML của máy ảo
 xml = f"""
 <interface type='bridge'>
  <mac address='{generate_random_mac()}'/>
  <source bridge='{bridge_name}'/>
  <virtualport type='openvswitch'/>
  <model type='virtio'/>
  <driver name="vhost"/>
  <address type='pci' domain='0x0000' bus='0x00' slot='{generate_pci_slot()}' function='0x0'/>
  <protocol family='ipv4'>
   <ip address='7.7.7.8' prefix='24'/>
   <route gateway='7.7.7.7'/>
  </protocol>
 </interface>
 """
 try:
  vm.attachDeviceFlags(xml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
  print(f"Đã thêm card mạng vào máy ảo '{vm_name}'.")
 except Exception as e:
  print(f"Lỗi khi thêm card mạng: {e}")
  return False
 return True

# Nhập tên máy ảo từ người dùng
vm_name = input("Nhập tên máy ảo: ")

# Nhập tên card mạng từ người dùng
bridge_name = input("Nhập tên card mạng: ")



# Tạo tên bridge OVS giống với tên card mạng


# Thêm card mạng vào máy ảo
if add_interface_to_vm(vm_name, bridge_name,ip_address_str):
 print(f"Đã thêm card mạng vào máy ảo '{vm_name}'.")