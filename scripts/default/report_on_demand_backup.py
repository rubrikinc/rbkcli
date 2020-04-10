"""Script to get all on-demand Backup events"""
from __future__ import division

import json

#from rbkcli import RbkCliBlackOps, RbkcliException
RbkcliException = NotImplementedError

from rbkcli import RbkCliBlackOps

import sys
import time

class OnDemandBackups(RbkCliBlackOps):

    method = 'get'  
    endpoint = '/report/on_demand/backup'
    description = str('Get all on-demand Backup events.')
    summary = 'List all Snapshots'
    parameters = [
        {
            'name': 'batch_size',
            'description': str('Amount of events to retrieve each bactch,'
                               ' default is 1000.'),
            'in': 'body',
            'required': False,
            'default': "300",
            'type': 'string'
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
            'name': 'out_file',
            'description': str('Path of the file which the output will be'
                               ' written'),
            'in': 'body',
            'required': True,
            'type': 'string'
        },        
    ]


    def execute(self, args):
        time_start = time.time()
        parameters = args['parameters']
        parameters = verify_params(self.parameters, parameters)

        setit = False
        results = []
        more = True
        after_id = ''
        on_d_str = "${onDemandBackupString}"
        end_date = ''
        event_counter = 0

        # Loop through the events and only store on-demand
        while more:
            cmd = str('event -q event_type=Backup,limit=%s,'
                      'after_date=%s' % (parameters['batch_size'],
                                         parameters['after_date']))
            if 'before_date' in parameters:
                cmd += ',before_date=%s' % parameters['before_date']
                end_date = parameters['before_date']
                setit = True


            if after_id:
                cmd += ',after_id=%s' % after_id

            backup_events = get_dicted(self.rbkcli.call_back(cmd))

            try:
                more = backup_events['hasMore']
                data = backup_events['data']
            except KeyError:
                RbkcliException(json.dumps(backup_events, indent=2))

            if data:

                last_date = data[-1]['time']
                if not end_date:
                    end_date = convert_current(last_date) + 'Z'

                for event in data:
                    event_counter += 1

                    if 'eventInfo' in event:

                        event_info = json.loads(event['eventInfo'])
                        event['eventInfo'] = event_info
                        
                        if on_d_str in event_info['params']:
                            if 'on demand' in event_info['params'][on_d_str]:
                                if event['eventStatus'] != 'Info':

                                    # Get event Series data
                                    series_id = event['eventSeriesId']
                                    
                                    cmd = 'event_series %s' % series_id
                                    series_data = get_dicted(
                                        self.rbkcli.call_back(cmd)
                                        )
                                    
                                    event['location'] = series_data['location']
                                    event['isOnDemand'] = True
                                    try:
                                        event['username'] = series_data['username']
                                    except KeyError:
                                        event['username'] = 'N/A'

                                    event['sla_name'] = series_data['slaName']
                                    event['sla_id'] = series_data['slaId']
                                    try:
                                        event['node_id'] = series_data['nodeIds']
                                    except KeyError:
                                        event['node_id'] = 'N/A'

                                    results.append(event)

                    #display_progress(parameters['after_date'][:-1],
                    #                 end_date[:-1],
                    #                 convert_current(event['time']),
                    #                 setit=setit)

                after_id = backup_events['data'][-1]['id']

                #print(parameters['after_date'])
                #print(end_date)

                display_progress(parameters['after_date'][:-1],
                                 end_date[:-1],
                                 convert_current(last_date),
                                 setit=setit)
            else:
                RbkcliException(json.dumps(backup_events, indent=2))
                more = False

        display_progress(parameters['after_date'][:-1],
                         end_date[:-1],
                         parameters['after_date'][:-1],
                         setit=setit)

        sys.stdout.write('\n')
        time_end = time.time()

        with open(parameters['out_file'], 'w') as output:
            output.write(json.dumps(results, indent=2))

        result = {
            'status': 'Completed successfully.',
            'json_report': parameters['out_file'],
            'events_verified': event_counter,
            'time_taken': str(int(int(time_end - time_start) / 60)) + ' mins'
        }
        return result

def verify_params(required_params, passed_params):
    for param in required_params:
        if param['required']:
            if param['name'] not in passed_params:
                raise RbkcliException('Missing parameter: %s \n' % param['name'] )
        else:
            if 'default' in param:
                passed_params[param['name']] = param['default']

    return passed_params


def get_dicted(result):
    """Convert json string from API response into dictionary."""
    return json.loads(result.text)

def represent_progress(progress):
    int_progress = int(progress)
    toolbar_width = 100

    #sys.stdout.write("[%s]" % ("_" * toolbar_width))
    #sys.stdout.flush()
    #sys.stdout.write("\b" * (toolbar_width+2))


    delta_empty = toolbar_width - int_progress
    empty =  "_" * delta_empty
    percentage_str = str("%.4f" % round(progress, 4)) + '%'
    
    sys.stdout.write("\b" * (toolbar_width + len(percentage_str) + 4))
    sys.stdout.write("[%s%s] %s" % ("=" * int_progress, empty, percentage_str))
    sys.stdout.flush()
    #sys.stdout.write("\b" * (toolbar_width + len(percentage_str) + 4))



def get_epoch(date):
    pattern = '%Y-%m-%dT%H:%M:%S'
    return int(time.mktime(time.strptime(date, pattern)))

def get_delta_epoch(start_date, end_date):
    start_epoch = get_epoch(start_date)
    end_epoch = get_epoch(end_date)
    return end_epoch - start_epoch

def get_epoch_current(current):
    pattern = '%a %b %d %H:%M:%S %Z %Y'
    return int(time.mktime(time.strptime(current, pattern)))

def convert_current(current):
    pattern = '%a %b %d %H:%M:%S %Z %Y'
    current_epoch = int(time.mktime(time.strptime(current, pattern)))
    pattern = '%Y-%m-%dT%H:%M:%S'
    return str(time.strftime(pattern, time.localtime(current_epoch)))

     
def display_progress(start_date, end_date, current, setit=False):

    #current = convert_current(current)
    delta_epoch = get_delta_epoch(start_date, end_date)
    current_epoch = get_delta_epoch(start_date, current)

    # print(start_date)
    # print(current)
    # print(end_date)

    if setit:
        delta_epoch += 3600


    delta_delta = delta_epoch - current_epoch

    progress = delta_delta / delta_epoch * 100

    represent_progress(progress)
