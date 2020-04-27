"""Script to get all on-demand Backup events"""
from __future__ import division

from datetime import datetime
import json

from rbkcli import RbkCliBlackOps, RbkcliException


import sys
import time


def timing(func):
    def wrapper(*arg, **kw):
        t1 = time.time()
        res = func(*arg, **kw)
        t2 = time.time()
        #print('    %s took about %s' % (func.__name__, str(t2 - t1)))
        return res
        #return (t2 - t1), res, func.__name__
    return wrapper


class MissedBackups(RbkCliBlackOps):
    method = 'get'  
    endpoint = '/report/missed/backup'
    description = str('Get all on-demand Backup events.')
    summary = 'List all Snapshots'
    parameters = [
        {
            'name': 'sla',
            'description': str('SLA or SLAs domain to fetch missed backups,'
                               ' default is all SLAs on SLA Compliance report.'),
            'in': 'body',
            'required': False,
            'default': "",
            'type': 'Array of strings'
        },
        {
            'name': 'object_type',
            'description': str('Type or types of objects to fetch missed backups,'
                               ' default is all objects on SLA Compliance report.'),
            'in': 'body',
            'required': False,
            'default': "",
            'type': 'Array of strings'
        },
        {
            'name': 'object_id',
            'description': str('Id or ids of objects to fetch missed backups,'
                               ' default is all objects on SLA Compliance report.'),
            'in': 'body',
            'required': False,
            'default': "",
            'type': 'Array of strings'
        },
        {
            'name': 'after_date',
            'description': str('Start date which the event will be fetched,'
                               ' the eldest event gathered will be from this'
                               ' date'),
            'in': 'body',
            'required': True,
            'type': 'string'
        },
        {
            'name': 'before_date',
            'description': str('End date which the event will be fetched, '
                               'the most recent event will be from this date,' 
                               ' default is today, 15 min ago.'),
            'in': 'body',
            'required': False,
            'type': 'string'
        },
        {
            'name': 'output_file',
            'description': str('Path of the file which the output will be'
                               ' written, default is local folder "missed'
                               '_backups_report.json"'),
            'in': 'body',
            'required': False,
            'default': 'missed_backups_report.json',
            'type': 'string'
        },        
    ]


    def execute(self, args):
        # Get passed paramters
        self.missed_backups = []
        self.passed_params = args['parameters']

        display_progress(1, 100, 'Getting SLA Report')

        # Get the SLA Compliance report as base
        self.report = self.get_sla_compliance_report()

        # Sort parameters and apply filters to report
        self.sort_params()
        
        time_start = time.time()
        pattern = '%Y-%m-%dT%H:%M:%S'
        #print('...Started at ' + time.strftime(pattern,
        #                                       time.localtime(time_start)))
        
        # Get SLA domains
        display_progress(2, 100, 'Getting SLA Domains')
        self.dict_sla = self.get_sla_domain()
        

        self.fetch_missed_backups()
        
        # Write final report
        display_progress(100, 100, 'Writing Output')
        with open(self.passed_params['output_file'], 'w') as my_out:
            my_out.write(json.dumps(self.missed_backups, indent=2))
        print('\n')

        #print('### Report created at %s' % self.passed_params['output_file'])
        return self.missed_backups

    def filter_object_report(self, key, values):
        new_report = []
        for snappable in self.report:
            for id_ in values:
                if id_ == snappable[key]:
                    new_report.append(snappable)

        self.report = new_report

    def fetch_missed_backups(self):
        weight_count = 3
        for snappable in self.report:

            display_progress(weight_count, 100, 'Getting Object Info')
            time_start = time.time()
            # print('# Started snappable [%s] (%s)' % (snappable['ObjectName'],
            #                                          snappable['ObjectId']))
            self.merge_missed_snaps(snappable)
            self.merge_missed_backups(snappable)
            time_end = time.time()
            # print('   completed in %s ' %
            #       str(int(int(time_end - time_start))) + ' secs. \n')
            #break
            weight_count += self.snap_weight

    @timing
    def merge_missed_backups(self, snappable):
        # print('   > Searching for Missed Backup Events')
        limit = 200
        after_date = self.passed_params['after_date']
        before_date = self.passed_params['before_date']
        protection_date = snappable['ProtectedOn'].replace(' ', 'T')

        # First event should be after protection date
        after_date = self.resolve_start_date(after_date, protection_date)

        # Get events for object
        cmd = str('event -q object_ids=%s,limit=%s,event_type=Backup,'
                  'after_date=%s,before_date=%s' % (snappable['ObjectId'],
                                                    str(limit),
                                                    after_date,
                                                    before_date           
                    )
                  )
        all_backups = self.loop_more_results(cmd)
        self.merge_skipped_date(all_backups, snappable, after_date,
                                before_date)


        #print(all_backups)

    def resolve_start_date(self, after_date, protected_date):
        """"""
        start_date_dict = {
            str(get_epoch_tdate(after_date)): after_date,
            str(get_epoch_tdate(protected_date)): protected_date,
        }
        result = max(get_epoch_tdate(after_date),
                     get_epoch_tdate(protected_date))
        return start_date_dict[str(result)]


    def merge_skipped_date(self, all_backups, snappable, after_date, before_date):
        # print('    - creating automated events')
        pattern = '%Y-%m-%dT%H:%M:%S'
        
        # Get SLA snapshot frequency in epoch
        sla_id = snappable['SlaDomainId']
        sla_frequencies = self.dict_sla[sla_id]['frequencies']
        
        freq_epoch = get_ingest_frequency(sla_frequencies)
        start_epoch = get_epoch_tdate(after_date)
        end_epoch = get_epoch_tdate(before_date)

        #print(start_epoch)
        #print(end_epoch)
        #print('Start Date: ' + after_date)
        #print('End Date: ' + before_date)

        epoch_counter = start_epoch
        anlys_start_epoch = start_epoch
        anlys_end_epoch = start_epoch + freq_epoch
        all_backups.reverse()
        new_event = {}

        for event in all_backups:
            event_epoch = get_epoch_sdate(event['time'])
            
            # print('    - start:' + str(anlys_start_epoch))
            # print('   ' + time.strftime(pattern, time.localtime(anlys_start_epoch)))
            # print('    - finish:' + str(anlys_end_epoch))
            # print('   ' + time.strftime(pattern, time.localtime(anlys_end_epoch)))
            # print('    - event:' + str(event_epoch))
            # print('   ' + time.strftime(pattern, time.localtime(event_epoch)))
            counter = 0
            if event_epoch < anlys_start_epoch:
                break
            while not (event_epoch >= anlys_start_epoch and event_epoch <= anlys_end_epoch):

                missed = time.strftime(pattern, time.gmtime(anlys_start_epoch))
                for k, v in snappable.items():
                    new_event[k] = v

                new_event['MissedSnapshotType'] = 'Automated Discovery'
                new_event['MissedSnapshotTime'] = missed
                new_event['extraInfo'] = str('A Backup event should have occurred until %s,'
                                             ' but the next backup event occurred at %s ' 
                                             % (time.strftime(pattern, time.gmtime(anlys_end_epoch-2)),
                                                time.strftime(pattern, time.gmtime(event_epoch-2))))
                new_event['ComplianceStatus'] = 'NonCompliant'
                self.missed_backups.append(new_event)
                #print('   - Limit: ' + time.strftime(pattern, time.gmtime(anlys_end_epoch)))
                #print('   - Event: ' + time.strftime(pattern, time.gmtime(event_epoch)))
                #print('   - Event Original: ' + event['time'])
                anlys_start_epoch += freq_epoch
                anlys_end_epoch += freq_epoch
                new_event = {}
                counter +=1
                if counter == 30:
                    print('    - had to break')
                    print('     More than 30 days missed backups, something'
                          ' is wrong with logic.')
                    print('   ' + time.strftime(pattern,
                                                time.gmtime(anlys_start_epoch)
                                                )
                        )
                    print(event)
                    break

            anlys_start_epoch += freq_epoch
            anlys_end_epoch += freq_epoch


    def loop_more_results(self, cmd, pager=['id', 'after_id']):
        all_results = []
        more = True
        new_cmd = cmd
        
        while more:
            try:
                # print('    - fetching new batch of events')
                result = get_dicted(self.rbkcli.call_back(new_cmd))
                if 'hasMore' not in result:
                    break
                more = result['hasMore']
                data = result['data']
                if more:
                    # Get the id of the last object
                    last_objct = data[-1][pager[0]]
                    new_cmd = '%s,%s=%s' % (cmd, pager[1], last_objct)
                all_results += data
                # print('    - fetched batch of events')
            except KeyboardInterrupt:
                more = False
        
        return all_results



    @timing
    def merge_missed_snaps(self, snappable):
        # print('   > Searching for Missed Snapshots')
        new_event = {}
        for k, v in snappable.items():
            new_event[k] = v
        api_cmd = self.resolve_object_api(snappable['ObjectType'],
                                          snappable['ObjectId'])

        missed_snaps = get_dicted(self.rbkcli.call_back(api_cmd))
        if 'data' in missed_snaps:
            if missed_snaps['data']:
                for missed_snap in missed_snaps['data']:
                    missed_type = 'Null'
                    extra_info = ''
                    if missed_snap['archivalLocationType'] and not missed_snap['missedSnapshotTimeUnits']:
                        missed_type = 'Archival' 
                        extra_info = missed_snap['archivalLocationType']

                    elif 'LOCAL' in missed_snap['archivalLocationType'] and missed_snap['missedSnapshotTimeUnits']:
                        missed_type = 'Acknoledged Miss' 
                        extra_info = missed_snap['archivalLocationType']
                    
                    new_event['MissedSnapshotType'] = missed_type
                    new_event['MissedSnapshotTime'] = missed_snap['missedSnapshotTime']
                    new_event['extraInfo'] = extra_info
                    self.missed_backups.append(new_event)
        else:
            print(missed_snaps)
        new_event = {}


    @timing
    def get_sla_compliance_report(self):

        # Get SLA Compliance
        cmd = 'report -f name~Compliance'

        reports = get_dicted(self.rbkcli.call_back(cmd))

        for report in reports:
            if report['name'] == 'SLA Compliance Summary' and report['reportType'] == 'Canned':

                cmd = 'jsonfy report_table -p report_id=%s,limit=9000' % report['id']
                report_content = get_dicted(self.rbkcli.call_back(cmd))
        
        return report_content

    @timing
    def get_sla_domain(self):
        dict_sla = {}
        slas = get_dicted(self.rbkcli.call_back('-v v2 sla_domain'))['data']
        for sla in slas:
            dict_sla[sla['id']] = sla
        return dict_sla

    def resolve_object_api(self, ob_type, ob_id):
        #id_refix = ob_id.split(':::')[0]
        object_type_api = {
            'LinuxFileset': 'fileset %s missed_snapshot' % ob_id,
            'ShareFileset': 'fileset %s missed_snapshot' % ob_id,
            'WindowsFileset': 'fileset %s missed_snapshot' % ob_id,
            'A': 'app_blueprint %s missed_snapshot' % ob_id,
            'B': 'aws ec2_instance %s missed_snapshot' % ob_id,
            'C': 'hyperv vm %s missed_snapshot' % ob_id,
            'D': 'nutanix vm %s missed_snapshot' % ob_id,
            'E': 'oracle db %s missed_snapshot' % ob_id,
            'F': 'storage array_volume_group %s missed_snapshot' % ob_id,
            'G': 'vcd vapp %s missed_snapshot' % ob_id,
            'WindowsVolumeGroup': 'volume_group %s missed_snapshot' % ob_id,
            'H': 'mssql db %s missed_snapshot' % ob_id,
            'VmwareVirtualMachine': 'vmware vm %s missed_snapshot' % ob_id,
        }

        return object_type_api[ob_type]

    def sort_params(self):

        for param in self.parameters:
            if param['required']:
                if param['name'] not in self.passed_params:
                    raise RbkcliException('Missing parameter: %s \n' %
                                          param['name'] )
            else:
                if param['name'] not in self.passed_params:
                    if 'default' in param:
                        self.passed_params[param['name']] = param['default']

        for params in ['sla', 'object_id', 'object_type']:
            if isinstance(self.passed_params[params], str):
                if self.passed_params[params]:
                    self.passed_params[params] = [self.passed_params[params]]

        if self.passed_params['object_id']:
            self.filter_object_report('ObjectId',
                                      self.passed_params['object_id'])

        if self.passed_params['sla']:
            self.filter_object_report('SlaDomain', self.passed_params['sla'])

        if self.passed_params['object_type']:
            self.filter_object_report('ObjectType',
                                      self.passed_params['object_type'])

        self.snap_weight = float(97 / len(self.report))


def get_ingest_frequency(frequencies):
    """Calculate the amount of seconds in a retention unit."""
    sec_dict = {
        'minute': 60,
        'hourly': 3600,
        'daily': 86400,
        'weekly': 604800,
        'monthly': 2592000,
        'quarterly': 7776000,
        'yearly': 31536000
    }
    secs = []

    for freq, freq_data in frequencies.items():
        secs.append(sec_dict[freq] * freq_data['frequency'])

    if not secs:
        secs = [0]
    return min(secs)


def get_dicted(result):
    """Convert json string from API response into dictionary."""
    return json.loads(result.text)

def represent_progress(progress, summary):
    int_progress = int(progress)
    toolbar_width = 100

    delta_empty = toolbar_width - int_progress
    empty =  "_" * delta_empty
    percentage_str = str("%.4f" % round(progress, 4)) + '%'
    
    sys.stdout.write("\b" * (toolbar_width + len(percentage_str) + 25))
    sys.stdout.write("%-20s [%s%s] %s" % 
                     (summary, "=" * int_progress, empty, percentage_str))
    sys.stdout.flush()

def get_epoch_tdate(date):
    try:
        date = date + ' UTC'
        pattern = '%Y-%m-%dT%H:%M:%S %Z'
        return int(time.mktime(time.strptime(date, pattern)))
    except ValueError:
        raise RbkcliException(date + ' Date is wrong.')

def get_delta_epoch(start_date, end_date):
    start_epoch = get_epoch_tdate(start_date)
    end_epoch = get_epoch_tdate(end_date)
    return end_epoch - start_epoch

def get_epoch_sdate(current):
    try:
        pattern = '%a %b %d %H:%M:%S %Z %Y'
        return int(time.mktime(time.strptime(current, pattern)))
    except ValueError:
        raise RbkcliException(date + ' Date is wrong.') 

def convert_current(current):
    pattern = '%a %b %d %H:%M:%S %Z %Y'
    current_epoch = int(time.mktime(time.strptime(current, pattern)))
    pattern = '%Y-%m-%dT%H:%M:%S'
    return str(time.strftime(pattern, time.localtime(current_epoch)))
     
def display_progress(weight_count, full_weigh, summary):

    try:
        progress = weight_count / full_weigh * 100
    except ZeroDivisionError:
        progress = 100

    represent_progress(progress, summary)


