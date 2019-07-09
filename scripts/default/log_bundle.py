"""rbkcli log bundle downloader"""

import json
import urllib3

from time import sleep
from rbkcli import RbkCliBlackOps


class LogBundle(RbkCliBlackOps):
    method = 'post'
    endpoint = '/log/bundle'
    description = str('Rbkcli command that generates log bundles and wait to'
                      ' download them.')
    summary = 'Generate rubrik log bundle'
    parameters = [
            {
            'name': 'location',
            'description': str('Location where the support bundle will be'
                               ' generated'),
            'in': 'body',
            'required': False,
            'type': 'string'
            }
        ]

    def execute(self, args):
        # Treat the parameter expected, if not provided save it to local.
        if 'location' in args.parameters.keys():
            location = str(args.parameters.location) + '/'
        else:
            location = ''

        # 1- Request log generation API:
        log_gen_job = self.rbkcli.call_back('support support_bundle -m post')

        # Treat api response as json.
        log_gen_job = json.loads(log_gen_job.text)

        # 2- Get log_job_id:
        log_job_id = log_gen_job['id']

        # 3- Verify log generation status:
        job_status =  self.rbkcli.call_back('support support_bundle -q id=' +
                                            log_job_id)

        # Treat api response as json.
        job_status = json.loads(job_status.text)
        
        print('Creating log bundle and waiting for the download, this could'
              ' take several minutes...')

        # 4- While job status is running, keep checking the status
        while (job_status['status'] == 'RUNNING' or
               job_status['status'] == 'QUEUED'):

            # wait the amount of seconds provided.
            sleep(30)

            # Call log generation job API again.
            job_status =  self.rbkcli.call_back('support support_bundle -q id='
                                                + log_job_id)

            # Treat api response as json.
            job_status = json.loads(job_status.text)

        # 5- Get the download link:
        down_url = job_status['links'][1]['href']

        # Get file name from download link.
        file_name = down_url.split('/')
        file_name = file_name[-1]

        # 6- Initiate the download
        pool = urllib3.PoolManager(cert_reqs='CERT_NONE')
        file = pool.request('GET', down_url, preload_content=False)
        
        # Save file to CWD.
        content = file.read()        
        open(location + file_name, 'wb').write(content)

        return job_status
