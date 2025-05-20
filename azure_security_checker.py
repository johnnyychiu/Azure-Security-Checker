import argparse
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient


def get_public_storage_blob_containers(storage_client):
    public_blobs = []
    accounts = storage_client.storage_accounts.list()
    for acc in accounts:
        try:
            props = storage_client.storage_accounts.get_properties(acc.id.split('/')[4], acc.name)
            if hasattr(props, 'allow_blob_public_access') and props.allow_blob_public_access:
                public_blobs.append({
                    'name': acc.name,
                    'location': acc.primary_location,
                    'resource_group': acc.id.split('/')[4]
                })
        except Exception as e:
            continue
    return public_blobs


def get_vms_with_public_ip(compute_client, network_client):
    vms = compute_client.virtual_machines.list_all()
    vms_with_public_ip = []
    for vm in vms:
        vm_name = vm.name
        resource_group = vm.id.split('/')[4]
        nics = vm.network_profile.network_interfaces
        for nic_ref in nics:
            nic_id = nic_ref.id
            nic_name = nic_id.split('/')[-1]
            try:
                nic = network_client.network_interfaces.get(resource_group, nic_name)
                for ip_config in nic.ip_configurations:
                    if ip_config.public_ip_address:
                        vms_with_public_ip.append({
                            'name': vm_name,
                            'resource_group': resource_group,
                            'public_ip': ip_config.public_ip_address.id.split('/')[-1]
                        })
            except Exception as e:
                continue
    return vms_with_public_ip


def get_overly_permissive_nsgs(network_client):
    nsgs = network_client.network_security_groups.list_all()
    risky_nsgs = []
    for nsg in nsgs:
        for rule in nsg.security_rules:
            if rule.direction == 'Inbound' and rule.access == 'Allow':
                if rule.source_address_prefix in ['0.0.0.0/0', '*']:
                    risky_nsgs.append({
                        'nsg_name': nsg.name,
                        'resource_group': nsg.id.split('/')[4],
                        'rule_name': rule.name,
                        'dest_port': rule.destination_port_range
                    })
    return risky_nsgs


def generate_report(public_blobs, vms_with_public_ip, risky_nsgs, output_file):
    with open(output_file, "w") as f:
        f.write("# Azure Security Checker Report\n\n")
        f.write("## Public Storage Accounts with Blob Public Access\n")
        if public_blobs:
            for item in public_blobs:
                f.write(f"- **{item['name']}** (Resource Group: {item['resource_group']}, Location: {item['location']})\n")
        else:
            f.write("- No public storage accounts with blob public access found.\n")
        f.write("\n## Virtual Machines with Public IP Addresses\n")
        if vms_with_public_ip:
            for item in vms_with_public_ip:
                f.write(f"- **{item['name']}** (Resource Group: {item['resource_group']}, Public IP: {item['public_ip']})\n")
        else:
            f.write("- No virtual machines with public IP addresses found.\n")
        f.write("\n## Network Security Groups with Overly Permissive Inbound Rules\n")
        if risky_nsgs:
            for nsg in risky_nsgs:
                f.write(f"- **{nsg['nsg_name']}** (Resource Group: {nsg['resource_group']}), Rule: {nsg['rule_name']}, Port: {nsg['dest_port']}\n")
        else:
            f.write("- No NSGs with risky inbound rules (0.0.0.0/0) found.\n")
    print(f"[+] Report generated: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Azure Security Checker - Advanced")
    parser.add_argument("--subscription", required=True, help="Azure subscription ID")
    parser.add_argument("--output", default="result.md", help="Output Markdown file")
    args = parser.parse_args()

    cred = DefaultAzureCredential()
    storage_client = StorageManagementClient(cred, args.subscription)
    compute_client = ComputeManagementClient(cred, args.subscription)
    network_client = NetworkManagementClient(cred, args.subscription)

    print("[*] Scanning for public blob storage accounts...")
    public_blobs = get_public_storage_blob_containers(storage_client)

    print("[*] Checking for virtual machines with public IP addresses...")
    vms_with_public_ip = get_vms_with_public_ip(compute_client, network_client)

    print("[*] Auditing NSGs for risky inbound rules (0.0.0.0/0)...")
    risky_nsgs = get_overly_permissive_nsgs(network_client)

    generate_report(public_blobs, vms_with_public_ip, risky_nsgs, args.output)


if __name__ == "__main__":
    main()
