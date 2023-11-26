import requests, shutil, smtplib, ssl
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


with open('GmailApiKey.txt', 'r') as file:
    api_key = file.readline().strip()
    app_password = file.readline().strip()
URL = "https://api.nasa.gov/planetary/apod?api_key=" + api_key

r = requests.get(URL)

data = r.json()

URL = None
try:
    URL = data["hdurl"]
except:
    URL = data["url"]

r = requests.get(URL, stream = True)
r.raw.decode_content = True

file = open('apodImage.jpg', 'wb')
shutil.copyfileobj(r.raw, file)
file.close()

subject = "NASA APOD " + data["date"]
body = data["explanation"]
sender_email = "justindurossdev@gmail.com"
email_file = open('emails.txt', 'r')

for line in email_file:
    receiver_email = line.strip()
    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    #message["Bcc"] = receiver_email  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    filename = "apodImage.jpg"  # In same directory as script

    # Open PDF file in binary mode
    with open(filename, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    # Encode file in ASCII characters to send by email
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )

    # Add attachment to message and convert message to string
    message.attach(part)
    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, app_password)
        server.sendmail(sender_email, receiver_email, text)
