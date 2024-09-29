import subprocess
import os

def run_ovs_command(command):
    """Chạy lệnh OVS với sudo và in kết quả."""
    try:
        subprocess.run(f"sudo {command}", shell=True, check=True)
        print(f"Thực hiện: {command} thành công.")
    except subprocess.CalledProcessError as e:
        print(f"Lỗi khi thực hiện: {command}. Chi tiết lỗi: {e}")

def modify_ovsx_file(x, y):
    """Chỉnh sửa file ovs{x}.xml để thêm portgroup với đúng định dạng thụt lề."""
    ovsx_file_path = f'/etc/libvirt/qemu/networks/ovs{x}.xml'
    vlan_y_portgroup = f"""
  <portgroup name='vlan-{y}00'>
    <vlan>
      <tag id='{y}00'/>
    </vlan>
  </portgroup>
    """

    vlan_all_tag = f"<tag id='{y}00'/>"
    vlan_all_portgroup = f"""
  <portgroup name='vlan-all'>
    <vlan trunk='yes'>
      <tag id='{x}00'/>
      <tag id='{y}00'/>
    </vlan>
  </portgroup>
    """

    if not os.path.exists(ovsx_file_path):
        print(f"File {ovsx_file_path} không tồn tại. Tạo file mới.")
        with open(ovsx_file_path, 'w') as file:
            file.write("<network>\n</network>")

    with open(ovsx_file_path, 'r+') as file:
        content = file.read()

        if f"<portgroup name='vlan-{y}00'>" not in content:
            print(f"Thêm portgroup 'vlan-{y}00' vào file.")
            content = content.replace("</network>", vlan_y_portgroup + "\n</network>")

        if "<portgroup name='vlan-all'>" not in content:
            print("Thêm portgroup 'vlan-all' vào file.")
            content = content.replace("</network>", vlan_all_portgroup + "\n</network>")
        else:
            print(f"Tìm và thêm <tag id='{y}00'/> vào portgroup 'vlan-all'.")
            start = content.find("<portgroup name='vlan-all'>")
            vlan_trunk_start = content.find("<vlan trunk='yes'>", start)
            vlan_trunk_end = content.find("</vlan>", vlan_trunk_start)
            updated_vlan_trunk = content[:vlan_trunk_end] + f"    {vlan_all_tag}\n" + content[vlan_trunk_end:]
            content = updated_vlan_trunk

        file.seek(0)
        file.write(content)
        file.truncate()


def modify_ovsy_file(x, y):
    """Chỉnh sửa file ovs{y}.xml, nhưng đổi vị trí biến x và y."""
    ovsy_file_path = f'/etc/libvirt/qemu/networks/ovs{y}.xml'
    vlan_x_portgroup = f"""
  <portgroup name='vlan-{x}00'>
    <vlan>
      <tag id='{x}00'/>
    </vlan>
  </portgroup>
    """

    vlan_all_tag = f"<tag id='{x}00'/>"
    vlan_all_portgroup = f"""
  <portgroup name='vlan-all'>
    <vlan trunk='yes'>
      <tag id='{y}00'/>
      <tag id='{x}00'/>
    </vlan>
  </portgroup>
    """

    if not os.path.exists(ovsy_file_path):
        print(f"File {ovsy_file_path} không tồn tại. Tạo file mới.")
        with open(ovsy_file_path, 'w') as file:
            file.write("<network>\n</network>")

    with open(ovsy_file_path, 'r+') as file:
        content = file.read()

        if f"<portgroup name='vlan-{x}00'>" not in content:
            print(f"Thêm portgroup 'vlan-{x}00' vào file.")
            content = content.replace("</network>", vlan_x_portgroup + "\n</network>")

        if "<portgroup name='vlan-all'>" not in content:
            print("Thêm portgroup 'vlan-all' vào file.")
            content = content.replace("</network>", vlan_all_portgroup + "\n</network>")
        else:
            print(f"Tìm và thêm <tag id='{x}00'/> vào portgroup 'vlan-all'.")
            start = content.find("<portgroup name='vlan-all'>")
            vlan_trunk_start = content.find("<vlan trunk='yes'>", start)
            vlan_trunk_end = content.find("</vlan>", vlan_trunk_start)
            updated_vlan_trunk = content[:vlan_trunk_end] + f"    {vlan_all_tag}\n" + content[vlan_trunk_end:]
            content = updated_vlan_trunk

        file.seek(0)
        file.write(content)
        file.truncate()



def redefine_and_restart_networks(x, y):
    """Redefine and restart the networks using virsh commands."""
    try:
        # Define and restart network ovs{x}
        run_ovs_command(f"virsh net-destroy ovs{x}")
        run_ovs_command(f"virsh net-define /etc/libvirt/qemu/networks/ovs{x}.xml")
        run_ovs_command(f"virsh net-start ovs{x}")
        run_ovs_command(f"virsh net-autostart ovs{x}")
        
        # Define and restart network ovs{y}
        run_ovs_command(f"virsh net-destroy ovs{y}")
        run_ovs_command(f"virsh net-define /etc/libvirt/qemu/networks/ovs{y}.xml")
        run_ovs_command(f"virsh net-start ovs{y}")
        run_ovs_command(f"virsh net-autostart ovs{y}")

    except Exception as e:
        print(f"Lỗi khi redefine và restart mạng: {e}")

def create_trunk_and_connect():
    """Tạo các trunk port và kết nối giữa hai switch, đồng thời chỉnh sửa file ovs{x}.xml và ovs{y}.xml."""
    x = input("Nhập số hoặc chữ cái cho switch đầu tiên (vd: 1, 2, a, b): ").strip()
    y = input(f"Nhập số hoặc chữ cái cho switch thứ hai mà br{x} muốn kết nối tới (vd: 1, 2, a, b): ").strip()

    trunk_xy = f"trk{x}{y}"  # Tạo tên trunk theo cú pháp trkXY
    trunk_yx = f"trk{y}{x}"  # Tạo tên trunk theo cú pháp trkYX

    # Thêm port trunk vào các bridge br{x} và br{y} + Kết hợp hai switch với nhau qua patch
    run_ovs_command(f"ovs-vsctl add-port br{x} {trunk_xy} -- set interface {trunk_xy} type=patch options:peer={trunk_yx}")
    run_ovs_command(f"ovs-vsctl add-port br{y} {trunk_yx} -- set interface {trunk_yx} type=patch options:peer={trunk_xy}")

    print(f"Switch br{x} và br{y} đã được kết hợp thông qua trunk.")

    # Chỉnh sửa file ovs{x}.xml và ovs{y}.xml để thêm các VLAN portgroup
    modify_ovsx_file(x, y)
    modify_ovsy_file(x, y)

    # Redefine và restart mạng ovs{x} và ovs{y}
    redefine_and_restart_networks(x, y)

def main():
    create_trunk_and_connect()

if __name__ == "__main__":
    main()
