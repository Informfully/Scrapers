from .mongomanager import MongoManager
from datetime import datetime
from smtplib import SMTP
from email.message import EmailMessage
from os import getenv
from uuid import uuid4

EMAIL_SUBJECT = 'Scraper Pipeline Error Notification'
EMAIL_TEMPLATE = '''Following error(s) have occured in scraper run {run_identifier}: {errors}'''

class Logger():
    def __init__(self, console_print=True):
        self.run_id = uuid4().hex
        self.log_list = []
        self.contains_error = False
        self.console_print = console_print

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if type:
            self.log(str(type) + str(value), 'Main Program', is_error=True)

        self.save_logs()
        return True

    def log(self, message, component, is_error=False):
        if self.console_print:
            if is_error:
                print(f"<{component}> -> Error: {message}")
            else:
                print(f"<{component}> -> {message}")

        if is_error:
            self.contains_error = True

        log_object = {
            'runId': self.run_id,
            'component': component,
            'message': message,
            'isError': is_error,
            'timestamp': datetime.now()
        }

        self.log_list.append(log_object)

    def save_logs(self):

        # Store logs into database
        with MongoManager() as db:
            db[getenv('COLLECTIONLOGS')].insert_many(self.log_list)

        # Send an email if an error has occured
        if self.contains_error and getenv('MAILONERROR') == 'True':
            msg = EmailMessage()
            msg['Subject'] = EMAIL_SUBJECT
            msg['From'] = getenv('MAILFROM')
            msg['To'] = getenv('MAILTO')

            errors_text = '\n'.join(
                [
                    f"{log['timestamp'].ctime()} | {log['component']} | {log['message']}"
                    for log in self.log_list if log['isError']
                ]
            )

            msg.set_content(
                EMAIL_TEMPLATE.format(
                    errors=errors_text,
                    run_identifier=self.run_id
                )
            )

            with SMTP(getenv('SMTPHOST'), getenv('SMTPPORT')) as smtp:
                smtp.starttls()
                smtp.login(getenv('SMTPUSER'), getenv('SMTPPASS'))
                smtp.send_message(msg)

            print('<Logger> -> Message: Error notification email has been sent')
