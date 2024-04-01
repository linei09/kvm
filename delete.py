import libvirt
import tkinter as tk
from tkinter import simpledialog
import xml.etree.ElementTree as ET
import time
import subprocess
def get_source_dev_by_mac(vm_name, mac_address):
    try:
        # Open connection to hypervisor
        conn = libvirt.open('qemu:///system')
        if conn is None:
            print('Failed to open connection to qemu:///system')
            return None

        # Find the domain by name
        domain = conn.lookupByName(vm_name)
        if domain is None:
            print(f"Virtual machine '{vm_name}' not found.")
            return None

        # Get current XML description
        xml_desc = domain.XMLDesc()

        # Parse XML
        root = ET.fromstring(xml_desc)

        # Iterate through interface elements to find the one with the given MAC address
        for iface in root.findall(".//devices/interface"):
            mac_elem = iface.find("mac")
            if mac_elem is not None and mac_elem.attrib.get('address') == mac_address:
                source_elem = iface.find("source")
                if source_elem is not None:
                    dev = source_elem.attrib.get('dev')
                    return dev

        print(f"No NIC found with MAC address '{mac_address}' in virtual machine '{vm_name}'.")
        return None

    except Exception as e:
        print(f"Error: {e}")
        return None
def create_nic_if_not_exists(nic_name, bridge_name):
    try:
        # Check if the NIC exists
        result = subprocess.run(["ip", "link", "show", nic_name], capture_output=True, text=True)
        if result.returncode != 0:
            # Create the NIC
            subprocess.run(["ip", "link", "add", "dev", nic_name, "type", "dummy"])
            print(f"NIC '{nic_name}' created.")
        
        # Check if the NIC is already added to the bridge
        result = subprocess.run(["ovs-vsctl", "list-ports", bridge_name], capture_output=True, text=True)
        if result.returncode == 0 and nic_name in result.stdout.splitlines():
            print(f"NIC '{nic_name}' already exists in bridge '{bridge_name}'.")
        else:
            # Add the NIC to the bridge
            subprocess.run(["ovs-vsctl", "add-port", bridge_name, nic_name])
            print(f"NIC '{nic_name}' added to bridge '{bridge_name}'.")

    except Exception as e:
        print(f"Failed to create or check NIC '{nic_name}': {e}")
def delete_host_nic(nic_name):
    try:
        # Check if the NIC exists
        result = subprocess.run(["ip", "link", "show", nic_name], capture_output=True, text=True)
        if result.returncode == 0:
            # Delete the NIC
            subprocess.run(["ip", "link", "delete", nic_name])
            print(f"NIC '{nic_name}' deleted.")
        else:
            print(f"NIC '{nic_name}' does not exist.")

    except Exception as e:
        print(f"Failed to delete NIC '{nic_name}': {e}")
        
def add_new_nic(vm_name, new_mac_address, new_source_dev):
    try:
        # Open connection to hypervisor
        conn = libvirt.open('qemu:///system')
        if conn is None:
            print('Failed to open connection to qemu:///system')
            return

        # Find the domain by name
        domain = conn.lookupByName(vm_name)
        if domain is None:
            print("Virtual machine '{}' not found.".format(vm_name))
            return

        # Get current XML description
        xml_desc = domain.XMLDesc()

        # Parse XML
        root = ET.fromstring(xml_desc)

        # Find the devices element to add the new NIC
        devices_elem = root.find(".//devices")
        if devices_elem is None:
            print("Devices element not found in XML.")
            return

        # Create new NIC XML using SubElement
        new_interface_elem = ET.SubElement(devices_elem, 'interface')
        new_interface_elem.set('type', 'direct')

        new_mac_elem = ET.SubElement(new_interface_elem, 'mac')
        new_mac_elem.set('address', new_mac_address)

        new_source_elem = ET.SubElement(new_interface_elem, 'source')
        new_source_elem.set('dev', new_source_dev)
        new_source_elem.set('mode', 'bridge')

        new_model_elem = ET.SubElement(new_interface_elem, 'model')
        new_model_elem.set('type', 'virtio')

        # Generate updated XML
        updated_xml_desc = ET.tostring(root, encoding='unicode')

        # Undefine the domain
        domain.undefine()

        # Define the domain again with updated XML description
        conn.defineXML(updated_xml_desc)

        print("New NIC added to virtual machine '{}' successfully.".format(vm_name))
    except Exception as e:
        print("Failed to add new NIC to virtual machine '{}': {}".format(vm_name, e))
    conn.close()


def edit_nic(vm_name, mac_to_edit=None, new_mac_address=None, new_source_dev=None):
    try:
        # Open connection to hypervisor
        conn = libvirt.open('qemu:///system')
        if conn is None:
            print('Failed to open connection to qemu:///system')
            return

        # Find the domain by name
        domain = conn.lookupByName(vm_name)
        if domain is None:
            print("Virtual machine '{}' not found.".format(vm_name))
            return

        # Get current XML description
        xml_desc = domain.XMLDesc()

        # Parse XML
        root = ET.fromstring(xml_desc)

        if mac_to_edit:
            # Find the network interface element with the given MAC address
            interface_elem = root.find(".//interface[@type='direct']/mac[@address='{}']/..".format(mac_to_edit))
            if interface_elem is None:
                print("Network interface with MAC address '{}' not found.".format(mac_to_edit))
                return
        else:
            # Find the first network interface element to edit
            interface_elem = root.find(".//interface[@type='direct']")
            if interface_elem is None:
                print("Network interface not found.")
                return

        # Update MAC address if provided
        if new_mac_address:
            mac_elem = interface_elem.find("mac")
            mac_elem.set("address", new_mac_address)

        # Update source device if provided
        if new_source_dev:
            source_elem = interface_elem.find("source")
            source_elem.set("dev", new_source_dev)

        # Generate updated XML
        updated_xml_desc = ET.tostring(root, encoding='unicode')

        # Undefine the domain
        domain.undefine()

        # Define the domain again with updated XML description
        conn.defineXML(updated_xml_desc)

        print("NIC configuration for virtual machine '{}' updated successfully.".format(vm_name))
    except Exception as e:
        print("Failed to update NIC configuration for virtual machine '{}': {}".format(vm_name, e))

    conn.close()


def edit_memory_cpu(vm_name, memory_mb=None, vcpu_count=None):
    try:
        # Open connection to hypervisor
        conn = libvirt.open('qemu:///system')
        if conn is None:
            print('Failed to open connection to qemu:///system')
            return

        # Find the domain by name
        domain = conn.lookupByName(vm_name)
        if domain is None:
            print("Virtual machine '{}' not found.".format(vm_name))
            return

        # Get current XML description
        xml_desc = domain.XMLDesc()

        # Parse XML
        root = ET.fromstring(xml_desc)

        if memory_mb is not None:
            # Update memory if provided
            memory_elem = root.find(".//memory")
            memory_elem.text = str(memory_mb * 1024)

        if vcpu_count is not None:
            # Update vCPU if provided
            vcpu_elem = root.find(".//vcpu")
            vcpu_elem.text = str(vcpu_count)

        # Generate updated XML
        updated_xml_desc = ET.tostring(root, encoding='unicode')

        # Undefine the domain
        domain.undefine()

        # Define the domain again with updated XML description
        conn.defineXML(updated_xml_desc)

        print("Memory and CPU configuration for virtual machine '{}' updated successfully.".format(vm_name))
    except Exception as e:
        print("Failed to update memory and CPU configuration for virtual machine '{}': {}".format(vm_name, e))

    conn.close()


def delete_nic(vm_name, mac_to_delete):
    try:
        # Open connection to hypervisor
        conn = libvirt.open('qemu:///system')
        if conn is None:
            print('Failed to open connection to qemu:///system')
            return

        # Find the domain by name
        domain = conn.lookupByName(vm_name)
        if domain is None:
            print("Virtual machine '{}' not found.".format(vm_name))
            return

        # Get current XML description
        xml_desc = domain.XMLDesc()

        # Parse XML
        root = ET.fromstring(xml_desc)

        # Find the network interface element with the given MAC address
        interface_elem = root.find(".//interface[@type='direct']/mac[@address='{}']/..".format(mac_to_delete))
        if interface_elem is None:
            print("Network interface with MAC address '{}' not found.".format(mac_to_delete))
            return

        # Remove the network interface element
        devices_elem = root.find(".//devices")
        devices_elem.remove(interface_elem)

        # Generate updated XML
        updated_xml_desc = ET.tostring(root, encoding='unicode')

        # Undefine the domain
        domain.undefine()

        # Define the domain again with updated XML description
        conn.defineXML(updated_xml_desc)

        print("NIC with MAC address '{}' deleted from virtual machine '{}' successfully.".format(mac_to_delete, vm_name))
    except Exception as e:
        print("Failed to delete NIC from virtual machine '{}': {}".format(vm_name, e))

    conn.close()




def get_vm_config_from_gui():
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    vm_name = simpledialog.askstring("Edit Virtual Machine", "Enter the name of the virtual machine to edit:")
    action1 = simpledialog.askstring("Edit Options", "Do you want to edit NIC or memory/CPU? (nic/memory_cpu):")
    if action1.lower() == 'nic':
        # Option to add, edit, or delete NIC
        action = simpledialog.askstring("Network Configuration", "Do you want to add, edit, or delete a NIC? (add/edit/delete):")
        if action.lower() == 'add':
            new_mac_address = simpledialog.askstring("Network Configuration", "Enter MAC address for the new NIC:")
            new_source_dev = simpledialog.askstring("Network Configuration", "Enter source device for the new NIC:")
            create_nic_if_not_exists(new_source_dev,new_source_dev)
            add_new_nic(vm_name, new_mac_address, new_source_dev)
            return
        elif action.lower() == 'edit':
            mac_to_edit = simpledialog.askstring("NIC Configuration", "Enter MAC address of the NIC to edit (leave blank to skip):")
            new_mac_address = simpledialog.askstring("NIC Configuration", "Enter new MAC address (leave blank to keep current):")
            new_source_dev = simpledialog.askstring("NIC Configuration", "Enter new source device (leave blank to keep current):")
            create_nic_if_not_exists(new_source_dev,new_source_dev)
            edit_nic(vm_name, mac_to_edit, new_mac_address, new_source_dev)
            return
        elif action.lower() == 'delete':
            mac_to_delete = simpledialog.askstring("Network Configuration", "Enter MAC address of the NIC to delete:")
            action3 = simpledialog.askstring("Delete Host NIC", "Do you want to this host NIC? (yes/no):")
            if action3.lower() == 'yes':
            	source_dev = get_source_dev_by_mac(vm_name, mac_to_delete)
            	delete_host_nic(source_dev)
            	delete_nic(vm_name, mac_to_delete)
            elif action3.lower() != 'yes':
            	delete_nic(vm_name, mac_to_delete)
            
            
            
            return
        else:
            print("Invalid action. Please choose 'add', 'edit', or 'delete'.")
        
    elif action1.lower() == 'memory_cpu':
        memory_mb_option = simpledialog.askstring("Memory", "Enter new memory size in MB (leave blank to keep current):")
        vcpu_count_option = simpledialog.askstring("CPU", "Enter new number of VCPUs (leave blank to keep current):")
        memory_mb = None if memory_mb_option.strip() == "" else int(memory_mb_option)
        vcpu_count = None if vcpu_count_option.strip() == "" else int(vcpu_count_option)
        edit_memory_cpu(vm_name, memory_mb, vcpu_count)
    else:
        print("Invalid action. Please choose 'nic' or 'memory_cpu'.")

def main():
    get_vm_config_from_gui()

if __name__ == "__main__":
    main()