"""Script to get all missed snapshots."""

import json

from rbkcli import RbkCliBlackOps, RbkcliException


class AllMissedSnaps(RbkCliBlackOps):

    method = 'get'  
    endpoint = '/snapshot/all/missed'
    description = str('Get all missed snapshots for all objects in CDM.')
    summary = 'Get all missed snapshots'
    parameters = []


    def execute(self, args):
        """."""
        self.all_snaps = []

        # Get all the type of objects that support a snapshot API call.
        get_snap_calls = 'commands -f "endpoint~{id} missed_snapshot,method=get"'
        snap_calls = get_dicted(self.rbkcli.call_back(get_snap_calls))

        # For each object type, get a list of all their objects.
        for calls in snap_calls:
            org_call = calls['endpoint'].split('{id}')[0]

            # If the object type is unmanged, ignore.
            if 'unmanaged' in org_call:
                continue

            objects = get_dicted(self.rbkcli.call_back(org_call))

            self.get_snap_from_objects(objects, org_call, calls)


        # Return all snaps and allow for filtering on rbkcli.
        return self.all_snaps

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


    def add_relevant_fields(self, snap, obj, keys, org_call):
        """."""
        snap['parent_object_id'] = obj[keys[0]]
        snap['parent_object_name'] = obj[keys[1]]
        snap['api_call'] = org_call

        return snap


def get_dicted(result):
    """Convert json string from API response into dictionary."""
    results = json.loads(result.text)
    if 'data' in results:
        results = results['data']
    return results
