"""Script to get all snapshots, its SLA and estimated expiration date"""

from datetime import datetime

from dateutil import parser
import json

from rbkcli import RbkCliBlackOps, RbkcliException


class AllSnaps(RbkCliBlackOps):

    method = 'get'  
    endpoint = '/snapshot/all'
    description = str('Get all snapshots from all objects in CDM.')
    summary = 'List all Snapshots'
    parameters = []


    def execute(self, args):
        """."""
        self.all_snaps = []
        self.slas = self.get_snap_max_life_per_sla()

        # Get all the type of objects that support a snapshot API call.
        get_snap_calls = 'commands -f "endpoint~{id} snapshot,method=get" -f'\
                         ' endpoint!~reference'
        snap_calls = get_dicted(self.rbkcli.call_back(get_snap_calls))

        # For each object type, get a list of all their objects.
        for calls in snap_calls:
            org_call = calls['endpoint'].split('{id}')[0]

            # If the object type is unmanged, ignore.
            if 'unmanaged' in org_call:
                continue

            objects = get_dicted(self.rbkcli.call_back(org_call))

            self.get_snap_from_objects(objects, org_call, calls)

        self.get_snaps_from_filesets()

        # Return all snaps and allow for filtering on rbkcli.
        return self.all_snaps

    def get_snap_max_life_per_sla(self):
        """."""
        slas_dict = {}
        slas_cmd = 'sla_domain -v v2'
        slas = get_dicted(self.rbkcli.call_back(slas_cmd))
        for sla in slas:
            freq_max = 'frequency_max_retention'
            sla[freq_max] = max_retention(sla['frequencies'])
            if sla[freq_max] == 0:
                sla[freq_max] = sla['maxLocalRetentionLimit']
            sla[freq_max] = str(sla[freq_max])
            slas_dict[sla['id']] = sla

        slas_dict['UNPROTECTED'] = {freq_max: 'FOREVER'}

        return slas_dict

    def get_snap_from_objects(self, objects, org_call, calls):
        """."""
        # For each object returned, get it's snapshots.
        for obj in objects:
            snaps = []
            try:
                snap_cmd = calls['endpoint'].replace('{id}', obj['id'])
                snaps = get_dicted(self.rbkcli.call_back(snap_cmd))

            except TypeError:
                pass
            
            # If there are snaps for the object improve their fields.
            if snaps:
                snapy = []
                for snap in snaps:
                    
                    snap = self.add_relevant_fields(snap, obj,
                                                    ['id', 'name'],
                                                    org_call)
                    snapy.append(snap)

                # Add each list of snaps to an accumulator.
                self.all_snaps += snapy


    def get_snaps_from_filesets(self):
        """."""
        # Filesets do not have a specific API for snapshots, but they
        # are listed under the details of each fileset object. 
        cmd = 'fileset -l id,name "fileset {id} -c snapshots"'
        fileset_snaps = get_dicted(self.rbkcli.call_back(cmd))
        for fileset_snap in fileset_snaps:
            keys = ['loop_id', 'loop_name']
            self.add_relevant_fields(fileset_snap, fileset_snap, keys,
                                     'fileset')

        # Add each list of snaps to an accumulator.
        self.all_snaps += fileset_snaps

    def add_relevant_fields(self, snap, obj, keys, org_call):
        """Add more context to snapshot."""
        snap['parent_object_id'] = obj[keys[0]]
        snap['parent_object_name'] = obj[keys[1]]
        snap['api_call'] = org_call
        try:
            max_retention = self.slas[snap['slaId']]['frequency_max_retention']
        except KeyError:
            max_retention = 'FOREVER-DELETED_SLAs'

        snap['estimate_expiration'] = self.gen_expiry_estimate(max_retention,
                                                               snap['date'])

        return snap

    def gen_expiry_estimate(self, max_retention, date):
        """Generate estimative of snapshot final date."""
        if 'FOREVER' not in max_retention:
            time = parser.parse(date)
            time_secs = time.strftime('%s')
            final_time = int(time_secs) + int(max_retention)
            max_retention = datetime.utcfromtimestamp(final_time).isoformat()

        return max_retention


def get_dicted(result):
    """Convert json string from API response into dictionary."""
    return json.loads(result.text)


def max_retention(frequencies):
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
        secs.append(sec_dict[freq] * freq_data['retention'])

    if not secs:
        secs = [0]
    return max(secs)
