import libvirt
import sys

def add_interface_to_vm(vm_name, network_name, interface_name, vlan):
    try:
        # Kết nối tới hypervisor KVM
        conn = libvirt.open('qemu:///system')
        if conn is None:
            print('Failed to open connection to qemu:///system', file=sys.stderr)
            exit(1)

        # Tìm kiếm máy ảo theo tên
        dom = conn.lookupByName(vm_name)
        if dom is None:
            print(f'No VM with the name {vm_name}', file=sys.stderr)
            exit(1)

        # Định nghĩa cấu hình interface dưới dạng XML, sử dụng network và VLAN
        interface_xml = f"""
        <interface type='network'>
            <source network='{network_name}' portgroup='{vlan}'/>
            <virtualport type='openvswitch'/>
            <target dev='{interface_name}'/>
            <model type='virtio'/>
            <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
        </interface>
        """

        # Gắn interface vào máy ảo và lưu cấu hình vĩnh viễn
        dom.attachDeviceFlags(interface_xml, libvirt.VIR_DOMAIN_AFFECT_LIVE | libvirt.VIR_DOMAIN_AFFECT_CONFIG)

        print(f'Interface {interface_name} with VLAN {vlan} has been added to {vm_name} and saved permanently.')

        # Đóng kết nối
        conn.close()

    except libvirt.libvirtError as e:
        print(f"Libvirt error: {str(e)}", file=sys.stderr)

# Nhập thông tin từ bàn phím
vm_name = input("Enter VM name: ")
network_name = input("Enter network name: ")
interface_name = input("Enter interface name: ")
vlan = input("Enter VLAN name: ")

add_interface_to_vm(vm_name, network_name, interface_name, vlan)
