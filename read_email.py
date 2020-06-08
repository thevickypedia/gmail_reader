import email
import imaplib
import os
import sys
from datetime import datetime, timedelta

u = os.getenv('user')
p = os.getenv('pass')

mail = imaplib.IMAP4_SSL('imap.gmail.com')  # connects to gmail using imaplib
mail.login(u, p)  # login to your gmail account using the env variables
mail.list()  # list all the folders within your mailbox (like inbox, sent, drafts, etc)
mail.select('inbox')  # selects inbox from the list

n = 0  # initiates count of emails
return_code, messages = mail.search(None, '(UNSEEN)')  # filters only unread emails
if return_code == 'OK':  # looks for "OK" in response
    for num in messages[0].split():
        n = n + 1  # add count of emails


def main():
    if n == 0:
        print('You have no unread emails.')
    else:
        # prints the number of emails and gets user confirmation before proceeding, press N/n to quit
        user_ip = input(f'You have {n} unread emails. Press Y/N to read emails:\n')
        if user_ip == 'Y' or user_ip == 'y':  # proceeds only if user input is Y or y
            i = 0
            if return_code == 'OK':
                for nm in messages[0].split():
                    i = i + 1
                    dummy, data = mail.fetch(nm, '(RFC822)')  # collects only the required part and stores it to "data"
                    for response_part in data:
                        if isinstance(response_part, tuple):  # checks for isinstance(__o, __t)
                            original_email = email.message_from_bytes(response_part[1])  # gets the rawest content
                            raw_receive = (original_email['Received'].split(';')[-1]).strip()  # gets raw received time
                            received_pdt = (raw_receive.split(',')[-1].split('-')[0]).strip()  # extracts datetime part
                            # converts pdt to cdt
                            datetime_obj = datetime.strptime(received_pdt, "%d %b %Y %H:%M:%S") + timedelta(hours=2)
                            receive = (datetime_obj.strftime("on %A, %B %d, %Y at %I:%M %p CDT"))  # formats datetime
                            raw_email = data[0][1]
                            raw_email_string = raw_email.decode('utf-8')  # decodes the raw email
                            email_message = email.message_from_string(raw_email_string)  # extracts message from string
                            # generates the file names in a directory tree by walking the tree bottom-up
                            # it yields a 3-tuple (body, sender, subject).
                            for part in email_message.walk():
                                if part.get_content_type() == "text/plain":  # ignore attachments/html
                                    # returns message's entire payload, a string or a message instance.
                                    # decode=true decodes the payload received.
                                    body = part.get_payload(decode=True)
                                    # gets sender email and subject and removes unnecessary white spaces
                                    sender = (original_email['From'] + '\n').strip()
                                    sub = (original_email['Subject'] + '\n').strip()
                                    msg = (body.decode('utf-8')).strip()  # decodes body of the email
                                    print(f"You have an email from {sender} with subject '{sub}' {receive}")
                                    #  gets user confirmation before printing the decoded body of the email
                                    get_user_input = input('Enter Y/N to read the email:\n')
                                    if get_user_input == 'Y' or get_user_input == 'y':
                                        print(f'{msg}\n')
                                    else:
                                        print(f'Privacy matters, body of the email from {sender} '
                                              'will not be displayed.\n')
                                    if i < n:  # proceeds only if loop count is less than the number of unread emails
                                        continue_confirmation = input('Enter Y/N to continue reading emails:\n')
                                        if continue_confirmation == 'N':
                                            sys.exit()
                                        elif continue_confirmation == 'n':
                                            sys.exit()
                                        else:
                                            pass


if __name__ == '__main__':
    main()
