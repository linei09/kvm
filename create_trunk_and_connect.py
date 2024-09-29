import subprocess

def run_ovs_command(command):
    """Chạy lệnh OVS với sudo và in kết quả."""
    try:
        subprocess.run(f"sudo {command}", shell=True, check=True)
        print(f"Thực hiện: {command} thành công.")
    except subprocess.CalledProcessError as e:
        print(f"Lỗi khi thực hiện: {command}. Chi tiết lỗi: {e}")

def create_trunk_and_connect():
    """Tạo các trunk port và kết nối giữa hai switch."""
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

def main():
    create_trunk_and_connect()

if __name__ == "__main__":
    main()
