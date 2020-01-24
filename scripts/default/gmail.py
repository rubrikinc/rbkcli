"""Module to send email using gmail APIs."""
import os
from rbkcli import RbkCliBlackOps, RbkcliException

try:
    from gmailer import Gmailer
except Exception as error:
    print('Could not import Gmailer libraries. Make sure you have installed'
          ' gmail packages: \n$ pip install google-api-python-client '
          'google-auth-httplib2 google-auth-oauthlib')

class GmailSender(RbkCliBlackOps):
    method = 'post'  
    endpoint = '/email'
    description = str('Send email using your pre-configured gmail '
                      'credentials.')
    summary = 'Send email message with gmail'
    parameters = [
        {
            'name': 'from',
            'description': str('Sender email address.'),
            'in': 'body',
            'required': True,
            'type': 'string'
        },
        {
            'name': 'to',
            'description': str('List of destination email addresses separated'
                               ' by semicolons ";".'),
            'in': 'body',
            'required': True,
            'type': 'string'
        },
        {
            'name': 'subject',
            'description': str('Subject of the email message'),
            'in': 'body',
            'required': True,
            'type': 'string'
        },
        {
            'name': 'files',
            'description': str('List of html files to be added to the email '
                               'message, separated by semicolons ";".'),
            'in': 'body',
            'required': True,
            'type': 'string'
        },

    ]


    def execute(self, args):
        """."""
        parameters = args['parameters']

        optional_parameter = {
            'EMAIL_CREDS': os.path.expanduser('~/google/credentials.json'),
            'PICKLE_TOKEN': os.path.expanduser('~/google/token.pickle')
        }


        for opt in ['EMAIL_CREDS', 'PICKLE_TOKEN']:
            if opt not in parameters:
                parameters[opt] = optional_parameter[opt]

        return sendit(**parameters)

def sendit(**parameters):
    try:
        parameters['to'] = parameters['to'].replace(';', ',')
        if ';' in parameters['files']:
            parameters['files'] = parameters['files'].split(';')
        else:
            parameters['files'] = [parameters['files']]

        sender = Gmailer(EMAIL_CREDS=parameters['EMAIL_CREDS'],
                         PICKLE_TOKEN=parameters['PICKLE_TOKEN'])

        msg = sender.emailit(parameters['from'],
                             parameters['to'],
                             parameters['subject'],
                             parameters['files'])

    except KeyError as error:
        msg = {
            'result': 'Failed to send message.',
            'error': 'ArgumentError # Missing argument ' + str(error)
        }
    except Exception as error:
        msg = {
            'result': 'Failed to send message.',
            'error': 'RunTimeError # Error running gmailer ' + str(error)
        }

    return msg
