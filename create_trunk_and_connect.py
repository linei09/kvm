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
    """Chỉnh sửa file ovsx.py để thêm portgroup với đúng định dạng thụt lề."""
    ovsx_file_path = '/etc/libvirt/qemu/networks/ovsx.py'
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
        print(f"File {ovsx_file_path} không tồn tại.")
        return

    with open(ovsx_file_path, 'r+') as file:
        content = file.read()

        # Thêm portgroup cho vlan-y00 nếu chưa có
        if f"<portgroup name='vlan-{y}00'>" not in content:
            print(f"Thêm portgroup 'vlan-{y}00' vào file.")
            content += vlan_y_portgroup

        # Kiểm tra và thêm vào portgroup vlan-all
        if "<portgroup name='vlan-all'>" not in content:
            print("Thêm portgroup 'vlan-all' vào file.")
            content += vlan_all_portgroup
        else:
            print(f"Tìm và thêm <tag id='{y}00'/> vào portgroup 'vlan-all'.")
            # Thêm <tag id='{y}00'/> vào đúng vị trí bên trong <vlan trunk='yes'>
            start = content.find("<portgroup name='vlan-all'>")
            vlan_trunk_start = content.find("<vlan trunk='yes'>", start)
            vlan_trunk_end = content.find("</vlan>", vlan_trunk_start)

            # Chèn tag mới vào bên trong thẻ <vlan trunk='yes'>
            updated_vlan_trunk = content[:vlan_trunk_end] + f"      {vlan_all_tag}\n" + content[vlan_trunk_end:]
            content = updated_vlan_trunk

        # Ghi lại file với nội dung đã chỉnh sửa
        file.seek(0)
        file.write(content)
        file.truncate()

def create_trunk_and_connect():
    """Tạo các trunk port và kết nối giữa hai switch, đồng thời chỉnh sửa file ovsx.py."""
    x = input("Nhập số hoặc chữ cái cho switch đầu tiên (vd: 1, 2, a, b): ").strip()
    y = input(f"Nhập số hoặc chữ cái cho switch thứ hai mà br{x} muốn kết nối tới (vd: 1, 2, a, b): ").strip()

    # Tạo trunk trkXY và trkYX
    trunk_xy = f"trk{x}{y}"  # Tạo tên trunk theo cú pháp trkXY
    trunk_yx = f"trk{y}{x}"  # Tạo tên trunk theo cú pháp trkYX

    # Tạo các bridge trunk trkXY và trkYX
    command = f"sudo ovs-vsctl add-br {trunk_xy}"
    run_ovs_command(command)
    
    command = f"sudo ovs-vsctl add-br {trunk_yx}"
    run_ovs_command(command)

    # Thêm port trunk vào các bridge tương ứng
    command = f"sudo ovs-vsctl add-port br{x} {trunk_xy}"
    run_ovs_command(command)

    command = f"sudo ovs-vsctl add-port br{y} {trunk_yx}"
    run_ovs_command(command)

    # Kết hợp hai switch với nhau qua patch
    command = f"sudo ovs-vsctl set interface {trunk_xy} type=patch options:peer={trunk_yx}"
    run_ovs_command(command)

    command = f"sudo ovs-vsctl set interface {trunk_yx} type=patch options:peer={trunk_xy}"
    run_ovs_command(command)

    print(f"Switch br{x} và br{y} đã được kết hợp thông qua trunk.")

    # Chỉnh sửa file ovsx.py để thêm các VLAN portgroup
    modify_ovsx_file(x, y)

def main():
    create_trunk_and_connect()

if __name__ == "__main__":
    main()
