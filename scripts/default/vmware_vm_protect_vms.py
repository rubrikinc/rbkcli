"""rbkcli protect vmware vms on csv"""

import json

from rbkcli import RbkCliBlackOps


class ProtectVmwareVms(RbkCliBlackOps):
    """
    Define the operation in rbkcli framework.

    Description:
    -Provide the structure of the endpoint being created  by this script,
     as if a RestFUL API endpoint, do it so by filling in the minimum
     necessary properties.

    Properties:
    -method = [string] The method by which this endpoint will be evoked
    -endpoint = [string] The /path/command_line to call this script
    -description = [string] A explanation of the main features of the script
    -summary = [string] A summarize explanation of the script
    -parameters = [list] of [dictionary] define the parameters  which are
    expected and used in the script.
    [
        {
            'name': '<parameter_name>',
            'description': 'Description of the parameter.',
            'in': 'Where to provide the parameter, could be [body, path]',
            'required': True/False (if its required to run the script),
            'type': 'data type of parameter
        }
    ]
    """
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
        """
        Method that calls operation from rbkcli framework.

        Description:
        -It will pass the variable args with the following structure:
        {
            'endpoint': 'path/command_line',
            'parameters': {
                '<parameter_name>': '<parameter_value>'
                },
            'method': 'get',
            'target': 'rbkcli target server',
            'query': '<query string passed>'
        }
        Once the variable args is a  DotDictionary its elements can be
        accessed as a property would be.
        Example:
            print(args.parameters.parameter_name)
        """
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
        vm_id_sla_id = []
        vm_sla = {}
        for csv_vm in csv_vms:
            for vm in vmware_vms:
                if (csv_vm['vmName'] == vm['name'] and
                        args.parameters.vcenter_id in vm['vcenterId']):
                    vm_sla['vmId'] = vm['id']
                    for sla in sla_domains:
                        if csv_vm['slaName'] == sla['name']:
                            vm_sla['slaId'] = sla['id']
                    vm_id_sla_id.append(vm_sla)
                    vm_sla = {}

                    # Loop ids into the SLA assign API.
        final_result = []
        for protection in vm_id_sla_id:
            long_cmd = str('sla_domain ' + protection['slaId'] + ' assign -m'
                                                                 ' post -p '
                                                                 'managedIds=['
                           + protection['vmId'] + ']')
            protection_result = self.rbkcli.call_back(long_cmd)
            final_result.append(json.loads(protection_result.text))

        return final_result
