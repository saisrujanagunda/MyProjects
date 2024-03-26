import os
import pickle
import base64
import json
# Gmail API utils
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
# for encoding/decoding messages in base64
from base64 import urlsafe_b64decode, urlsafe_b64encode
# for dealing with attachement MIME types
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from mimetypes import guess_type as guess_mime_type

# Request all access (permission to read/send/receive emails, manage the inbox, and more)
SCOPES = ['https://mail.google.com/']
our_email = 'gsaisrujana@gmail.com'


def gmail_authenticate():
    creds = None
    # the file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # if there are no (valid) credentials availablle, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)

# get the Gmail API service
service = gmail_authenticate()

#searching emails
def search_messages(service, query):
    all_results = []
    for q in query:
        result = service.users().messages().list(userId='me',q=q).execute()
        messages = []
        if 'messages' in result:
            messages.extend(result['messages'])
        while 'nextPageToken' in result:
            page_token = result['nextPageToken']
            result = service.users().messages().list(userId='me',q=q, pageToken=page_token).execute()
            if 'messages' in result:
                messages.extend(result['messages'])
        all_results.extend(messages)
    return all_results

    
#reading emails
def read_message(service, message, json_data):
    """
    This function takes Gmail API `service`, a message, and a JSON data list.
    It extracts the email body from the message and adds it to the JSON data list.
    """
    msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
    payload = msg['payload']
    parts = payload.get("parts")
    if parts:
        for part in parts:
            mimeType = part.get("mimeType")
            if mimeType == "text/plain":
                body = part.get("body")
                data = body.get("data")
                if data:
                    text = base64.urlsafe_b64decode(data).decode('utf-8')
                    # Add email body to the JSON data list
                    json_data.append({'email_body': text})
                    break  # Exit loop after printing the first plain text part

# Create a list to store email data
email_data = []

# Get emails that match the query
query = ["Unfortuantely", "not selected", "pursue others", "regret to inform", "move forward with other candidates"]
results = search_messages(service, query)
print(f"Found {len(results)} results.")

# For each email matched, read it and add its body to the email data list
for msg in results:
    read_message(service, msg, email_data)

# Write email data to a JSON file
with open('emails.json', 'w') as json_file:
    json.dump(email_data, json_file, indent=4)
