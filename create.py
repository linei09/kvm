import libvirt
from subprocess import run

def create_disk_image(image_path, size_in_gib):
    """
    Tạo một ổ đĩa ảo (qcow2) với kích thước đã cho.

    Args:
      image_path (str): Đường dẫn đến tệp ảnh.
      size_in_gib (int): Kích thước của ổ đĩa ảo trong GiB.
    """
    # Chuyển đổi kích thước từ GiB sang byte
    size_in_bytes = size_in_gib * 1024 * 1024 * 1024

    # Sử dụng lệnh qemu-img để tạo tệp qcow2
    run(["qemu-img", "create", "-f", "qcow2", image_path, str(size_in_bytes)])

    print(f"Tạo thành công ổ đĩa ảo: {image_path}")
def create_vm(vm_name, memory, vcpu, disk_path, disk_size, os_iso):
    conn = libvirt.open('qemu:///system')  # Mở kết nối tới libvirt

    # Tạo ổ đĩa nếu chưa tồn tại
    try:
        open(disk_path)
    except FileNotFoundError:
        create_disk_image(disk_path, disk_size)

    # Tạo định dạng XML cho máy ảo
    xml_config = """
    <domain type='kvm'>
        <name>{}</name>
        <memory unit='KiB'>{}</memory>
        <vcpu placement='static'>{}</vcpu>
        <os>  
            <type arch='x86_64' machine='pc'>hvm</type>
            <boot dev='hd'/>  
            <boot dev='cdrom'/>
        </os>
        <devices>
            <disk type='file' device='disk'>
                <driver name="qemu" type="qcow2"/>
                <source file='{}'/>
                <target dev='vda' bus='virtio'/>


            </disk>
            <disk type='file' device='cdrom'>
        <driver name="qemu" type="raw"/>
                <source file='{}'/>
                <target dev="sda" bus="sata"/>
                <readonly/>


            </disk>
            <interface type='network'>
                <source network='default'/>
            </interface>
            <graphics type='vnc' port='-1' autoport='yes' listen='0.0.0.0'/>
        </devices>
    </domain>
    """.format(vm_name, memory * 1024, vcpu, disk_path, os_iso)

    # Tạo máy ảo từ định dạng XML
    vm = conn.createXML(xml_config, 0)

    conn.close()

# Sử dụng hàm để tạo máy ảo
vm_name = input("Nhập tên cho máy ảo: ")
disk_path = f"/var/lib/libvirt/images/{vm_name}.qcow2"
create_vm(vm_name, 2048, 2, disk_path, 20, "/home/ubuntu/Downloads/ubuntu-22.04.4-desktop-amd64.iso")