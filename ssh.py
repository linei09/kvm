import paramiko
import time

def ssh_and_assign_ip_with_password(hostname, username, password, network_interface, ip_address, netmask, gateway):
    # Tạo SSH client
    ssh = paramiko.SSHClient()
    
    # Tự động thêm host key nếu chưa có
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Kết nối tới máy ảo sử dụng username và password
        ssh.connect(hostname=hostname, username=username, password=password)

        # Mở một shell tương tác
        ssh_shell = ssh.invoke_shell()

        # Gửi lệnh để gán IP cho card mạng, sử dụng sudo với tùy chọn -S
        ssh_shell.send(f"echo {password} | sudo -S ip addr add {ip_address}/{netmask} dev {network_interface}\n")
        time.sleep(1)  # Cho thời gian để lệnh thực thi
        ssh_shell.send(f"echo {password} | sudo -S ip route add default via {gateway}\n")
        time.sleep(1)  # Cho thời gian để lệnh thực thi

        # Đọc output từ shell
        output = ssh_shell.recv(1024).decode()
        print(output)

        if "password" in output.lower() or "error" in output.lower():
            print(f"Lỗi khi gán IP: {output}")
        else:
            print(f"Thành công: {output}")
    
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")
    
    finally:
        # Đóng kết nối SSH
        ssh.close()

# Thông tin máy ảo và card mạng
hostname = "192.168.122.168"
username = "ubuntu"
password = "1"
network_interface = "enp7s0"  # ví dụ: eth0 hoặc ens3
ip_address = "192.168.1.100"
netmask = "24"
gateway = "192.168.1.1"

# Thực hiện gán IP cho card mạng
ssh_and_assign_ip_with_password(hostname, username, password, network_interface, ip_address, netmask, gateway)
