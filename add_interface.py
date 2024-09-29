import libvirt
import sys
import xml.etree.ElementTree as ET

def add_interface_to_vm(vm_name, network_name, vlan):
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

        # Lấy XML hiện tại của máy ảo để lưu lại các interface trước khi thêm
        tree = ET.fromstring(dom.XMLDesc())
        current_interfaces = set()
        for iface in tree.findall("devices/interface/target"):
            current_interfaces.add(iface.attrib['dev'])

        # Định nghĩa cấu hình interface dưới dạng XML, sử dụng network và VLAN
        interface_xml = f"""
        <interface type='network'>
            <source network='{network_name}' portgroup='{vlan}'/>
            <model type='virtio'/>
        </interface>
        """

        # Gắn interface vào máy ảo và lưu cấu hình vĩnh viễn
        dom.attachDeviceFlags(interface_xml, libvirt.VIR_DOMAIN_AFFECT_LIVE | libvirt.VIR_DOMAIN_AFFECT_CONFIG)

        print(f'Interface with VLAN {vlan} has been added to {vm_name} and saved permanently.')

        # Lấy lại XML sau khi thêm interface
        tree = ET.fromstring(dom.XMLDesc())
        new_interfaces = set()
        for iface in tree.findall("devices/interface/target"):
            new_interfaces.add(iface.attrib['dev'])

        # Tìm interface mới được thêm
        added_interface = new_interfaces - current_interfaces
        if added_interface:
            print(f"New interface(s) created: {', '.join(added_interface)}")
        else:
            print("No new interface found. It might not have been attached correctly.")

        # Force off máy ảo
        if dom.isActive():
            print(f"Force off VM {vm_name}...")
            dom.destroy()  # Force off the VM

        # Khởi động lại máy ảo
        print(f"Starting VM {vm_name} again...")
        dom.create()

        # Đóng kết nối
        conn.close()

    except libvirt.libvirtError as e:
        print(f"Libvirt error: {str(e)}", file=sys.stderr)

# Nhập thông tin từ bàn phím
vm_name = input("Enter VM name: ")
network_name = input("Enter network name: ")
vlan = input("Enter VLAN name: ")

add_interface_to_vm(vm_name, network_name, vlan)
