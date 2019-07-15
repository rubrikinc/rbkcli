"""rbkcli protect vmware vms on csv"""

import json

from rbkcli import RbkCliBlackOps


class ProtectVmwareVms(RbkCliBlackOps):
    method = 'post'
    endpoint = '/vmware/vm/protect/vms'
    description = str('Rbkcli command that assign VMs to the respective SLA '
                      'domain defined in the csv file')
    summary = 'Assign VMware vms to SLA domain.'
    parameters = [
            {
            'name': 'vcenter_id',
            'description': 'ID of the vcenter where the VMs reside.',
            'in': 'body',
            'required': True,
            'type': 'string'
            },
            {
            'name': 'csv',
            'description': 'Path to csv file of the VMs',
            'in': 'body',
            'required': True,
            'type': 'string'
            }
        ]

    def execute(self, args):
        # Treat the parameter expected, if not provided raise error.
        if 'vcenter_id' not in args.parameters.keys():
            raise Exception('Missing args')
        if 'csv' not in args.parameters.keys():
            raise Exception('Missing args')

        # Get all the vms
        vmware_vms = self.rbkcli.call_back('vmware vm -s id,name,vcenterId')
        vmware_vms = json.loads(vmware_vms.text)

        # Get all the SLAs
        sla_domains = self.rbkcli.call_back('sla_domain -s id,name')
        sla_domains = json.loads(sla_domains.text)

        # Load CSV as json
        csv_vms = self.rbkcli.call_back('jsonfy csv -p file=' +
                                        args.parameters.csv)
        csv_vms = json.loads(csv_vms.text)

        # Resolve name id of VMs and SLAs
        vmid_slaid = []
        vm_sla = {}
        for csv_vm in csv_vms:
            for vm in vmware_vms:
                if (csv_vm['vmName'] == vm['name'] and
                    args.parameters.vcenter_id in vm['vcenterId']):
                    vm_sla['vmId'] = vm['id']
                    for sla in sla_domains:
                        if csv_vm['slaName'] == sla['name']:
                            vm_sla['slaId'] = sla['id']
                    vmid_slaid.append(vm_sla)
                    vm_sla = {}       

        # Loop ids into the SLA assing API.
        final_result = []
        for protection in vmid_slaid:
            long_cmd = str('sla_domain ' + protection['slaId'] + ' assign -m'
                           ' post -p managedIds=[' + protection['vmId'] + ']')
            protection_result = self.rbkcli.call_back(long_cmd)
            final_result.append(json.loads(protection_result.text))

        return final_result
