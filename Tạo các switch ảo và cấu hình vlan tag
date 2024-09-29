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
    command = f"ovs-vsctl add-br {switch_name}"
    run_ovs_command(command)
    print(f"Switch {switch_name} đã được tạo thành công.")

def main():
    create_virtual_switch()

if __name__ == "__main__":
    main()
