
from rbkcli import RbkCliBlackOps, RbkcliException

try:
    from gmailer import Gmailer
except Exception as error:
    print('Could not import Gmailer libraries.')

class GmailSender(RbkCliBlackOps):

    method = 'post'  
    endpoint = '/email'
    description = str('Send email using your pre-configured gmail credentials.')
    summary = 'Send email message with gmail'
    parameters = []


    def execute(self, args):
        """."""
        parameters = args['parameters']

        optional_parameter = {
            'EMAIL_CREDS': '~/google/credentials.json',
            'PICKLE_TOKEN': '~/google/token.pickle'
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