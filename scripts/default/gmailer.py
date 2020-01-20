"""Send an email message from the user's account.
"""
import pickle

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import base64
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
import os

from apiclient import errors


class Gmailer:
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    EMAIL_CREDS = 'credentials.json'
    PICKLE_TOKEN = 'token.pickle'

    def __init__(self, **config):
        self.config = config
        self.__load_configs()
        self.service = self.__get_gmail_service()

    def __load_configs(self):
        for conf in ['EMAIL_CREDS', 'PICKLE_TOKEN']:
            try:
                setattr(Gmailer, conf, self.config[conf])
            except Exception as error:
                print(error)

    def __send_message(self, message, user_id='me'):
        """Send an email message.

        Args:
            service: Authorized Gmail API service instance.
            user_id: User's email address. The special value "me"
            can be used to indicate the authenticated user.
            message: Message to be sent.

        Returns:
            Sent Message.
        """
        try:
            message = (self.service.users().messages()
                       .send(userId=user_id, body=message)
                       .execute())
            #print('Message Id: %s' % message['id'])
            return message
        except errors.HttpError as error:
            print('An error occurred: %s' % error)


    def __create_message(self, sender, to, subject, msg_text, m_type='html'):
        """Create a message for an email.

        Args:
            sender: Email address of the sender.
            to: Email address of the receiver.
            subject: The subject of the email message.
            msg_text: The text of the email message.

        Returns:
            An object containing a base64url encoded email object.
        """
        message = MIMEText(msg_text, m_type)
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        
        return {'raw': base64.urlsafe_b64encode(message.as_string()
                                                .encode('UTF-8'))
                                                .decode('ascii')}
        #return {'raw': base64.urlsafe_b64encode(message.as_bytes())}


    def __create_msg_attachment(self, sender, to, subject, msg_text, file_dir,
                                    filename):
        """Create a message for an email.

        Args:
            sender: Email address of the sender.
            to: Email address of the receiver.
            subject: The subject of the email message.
            msg_text: The text of the email message.
            file_dir: The directory containing the file to be attached.
            filename: The name of the file to be attached.

        Returns:
            
        """
        message = MIMEMultipart()
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject

        msg = MIMEText(msg_text)
        message.attach(msg)

        path = os.path.join(file_dir, filename)
        content_type, encoding = mimetypes.guess_type(path)

        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'
            main_type, sub_type = content_type.split('/', 1)
        if main_type == 'text':
            fp = open(path, 'rb')
            msg = MIMEText(fp.read(), _subtype=sub_type)
            fp.close()
        elif main_type == 'image':
            fp = open(path, 'rb')
            msg = MIMEImage(fp.read(), _subtype=sub_type)
            fp.close()
        elif main_type == 'audio':
            fp = open(path, 'rb')
            msg = MIMEAudio(fp.read(), _subtype=sub_type)
            fp.close()
        else:
            fp = open(path, 'rb')
            msg = MIMEBase(main_type, sub_type)
            msg.set_payload(fp.read())
            fp.close()

        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        message.attach(msg)

        return {'raw': base64.urlsafe_b64encode(message.as_string())}

    def __get_gmail_service(self):
        """Shows basic usage of the Gmail API.
        Lists the user's Gmail labels.
        """
        creds = None
        # The file token.pickle stores the user's access and refresh tokens,
        # and is created automatically when the authorization flow completes
        # for the first time.
        if os.path.exists(self.PICKLE_TOKEN):
            with open(self.PICKLE_TOKEN, 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.EMAIL_CREDS, self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.PICKLE_TOKEN, 'wb') as token:
                pickle.dump(creds, token)

        return build('gmail', 'v1', credentials=creds)

    def __load_html_str(self, html_files):
        html_body = ''
        for file in html_files:
            with open(file, 'r') as ms:
                html_body += ms.read()
        return html_body

    def emailit(self, sender, to, subject, html_files):
        html_body = self.__load_html_str(html_files)
        msg = self.__create_message(sender, to, subject, html_body)
        msg_id = self.__send_message(msg)['id']

        return {
            'result': 'Successfully sent message.',
            'message_info': {
                'from': sender,
                'to': to,
                'subject': subject,
                'body': html_files,
                'msg_id': msg_id
            }
        }


if __name__ == '__main__':
    files = [
        '/tmp/report.html'
    ]
    
    sender = Gmailer(EMAIL_CREDS='/tmp/google/credentials.json',
                     PICKLE_TOKEN='/tmp/google/token.pickle')
    msg = sender.emailit('sender@gmail.com',
                         'dest@gmail.com',
                         'ReportTest',
                          files)
