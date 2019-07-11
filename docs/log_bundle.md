
# /scripts/log/bundle
This is a custom script created to facilitate the log gathering and also elucidate how simple it is to create a new command line.

1. The code:
    ```python
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
    ```
2. Usage:
    ```
    $ rbkcli log bundle -m post -p location="./Downloads"
    Creating log bundle and downloading it, this could take several minutes...
    {
      "id": "SUPPORT_BUNDLE_GENERATOR_24f2a096-0627-445c-a029-da5b8aa00492_58daa55b-ff64-4721-8596-84b7ac887d9c:::0",
      "status": "SUCCEEDED",
      "startTime": "2019-06-14T15:18:39.075Z",
      "endTime": "2019-06-14T15:23:07.757Z",
      "nodeId": "cluster:::RVMHM184S001650",
      "links": [
        {
          "href": "https://192.168.75.200/api/internal/support/support_bundle?id=SUPPORT_BUNDLE_GENERATOR_24f2a096-0627-445c-a029-da5b8aa00492_58daa55b-ff64-4721-8596-84b7ac887d9c:::0",
          "rel": "self"
        },
        {
          "href": "https://192.168.75.200/support_bundle/rubrik_logs-2019-06-14-15-18-39.tar.gz",
          "rel": "result"
        }
      ]
    }
    ```

3. Results:
    ```
    $ ll Downloads/
    total 1028536
    drwxr-xr-x  2 bmanesco bmanesco       4096 Jun 14 16:31 ./
    drwxr-xr-x 19 bmanesco bmanesco       4096 Jun 14 16:26 ../
    -rw-rw-r--  1 bmanesco bmanesco 1053208190 Jun 14 16:31 rubrik_logs-2019-06-14-15-26-46.tar.gz
    ```

