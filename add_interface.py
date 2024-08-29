import libvirt
import sys

def add_interface_to_vm(vm_name, bridge_name, interface_name):
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

        # Định nghĩa cấu hình interface dưới dạng XML
        interface_xml = f"""
        <interface type='bridge'>
            <source bridge='{bridge_name}'/>
            <virtualport type='openvswitch'/>
            <target dev='{interface_name}'/>
            <model type='virtio'/>
        </interface>
        """

        # Gắn interface vào máy ảo và lưu cấu hình vĩnh viễn
        dom.attachDeviceFlags(interface_xml, libvirt.VIR_DOMAIN_AFFECT_LIVE | libvirt.VIR_DOMAIN_AFFECT_CONFIG)

        print(f'Interface {interface_name} has been added to {vm_name} and saved permanently.')

        # Đóng kết nối
        conn.close()

    except libvirt.libvirtError as e:
        print(f"Libvirt error: {str(e)}", file=sys.stderr)

# Gọi hàm với tên máy ảo, bridge và tên interface muốn thêm
vm_name = "truc1"
bridge_name = "br0"
interface_name = "eth11"

add_interface_to_vm(vm_name, bridge_name, interface_name)
