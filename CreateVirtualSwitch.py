import subprocess

def run_ovs_command(command):
    """Chạy lệnh OVS và in kết quả."""
    try:
        subprocess.run(f"sudo {command}", shell=True, check=True)
        print(f"Thực hiện: {command} thành công.")
    except subprocess.CalledProcessError as e:
        print(f"Lỗi khi thực hiện: {command}. Chi tiết lỗi: {e}")

def create_virtual_switch():
    """Tạo một switch ảo với tên theo cú pháp brx."""
    x = input("Nhập một số hoặc chữ cái cho switch (vd: 1, 2, a, b): ").strip()
    switch_name = f"br{x}"  # Tạo tên bridge theo cú pháp brx
    command = f"sudo ovs-vsctl add-br {switch_name}"
    run_ovs_command(command)
    print(f"Switch {switch_name} đã được tạo thành công.")
    create_libvirt_network_xml(x)

def create_libvirt_network_xml(x):
    """Tạo file XML trong thư mục /etc/libvirt/qemu/networks/ovs{x}.xml với quyền sudo."""
    network_xml = f"""
<network>
  <name>ovs{x}</name>
  <forward mode='bridge'/>
  <bridge name='br{x}'/>
  <virtualport type='openvswitch'/>
  <portgroup name='vlan-00' default='yes'>
  </portgroup>
  <portgroup name='vlan-{x}00'>
    <vlan>
      <tag id='{x}00'/>
    </vlan>
  </portgroup>
</network>
"""
    # Đường dẫn đến file XML
    xml_file_path = f"/etc/libvirt/qemu/networks/ovs{x}.xml"
    
    # Dùng sudo tee để ghi vào file với quyền sudo
    try:
        process = subprocess.Popen(['sudo', 'tee', xml_file_path], stdin=subprocess.PIPE)
        process.communicate(input=network_xml.encode())
        print(f"File {xml_file_path} đã được tạo thành công.")
    except Exception as e:
        print(f"Lỗi khi tạo file XML: {e}")

def main():
    create_virtual_switch()

if __name__ == "__main__":
    main()
