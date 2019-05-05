import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

smtp_server = "smtp.office365.com"
port = 587  # For starttls
sender_email = "etu27397@henallux.be"
from_address = "etu27397@student.henallux.be"
password = ""

# Create a secure SSL context
context = ssl.create_default_context()


def notify_user(job, new_state):
    # Try to log in to server and send email
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.ehlo()  # Can be omitted
        server.starttls(context=context)  # Secure the connection
        server.ehlo()  # Can be omitted
        server.login(sender_email, password)
        # TODO: Send email here
        msg = MIMEMultipart()
        msg['From'] = from_address
        msg['To'] = job['user_input']['user_mail']
        msg['Subject'] = "Job state update"
        body = """      
        Dear {},
        
        Your job submitted to {} (ID: {}) has changed status to the current status {}.
        
        Sincerely
        
        The partially annoyed automated Python server
        """.format(job['user_input']['username'], job['destination_cluster']['name'],
                   job['job_uuid'], new_state['state'])

        msg.attach(MIMEText(body, 'plain'))

        message = msg.as_string()
        server.sendmail(from_address, job['user_input']['user_mail'], message)

    except Exception as e:
        raise Exception("Unable to send mail - Error: {}".format(e))
    finally:
        server.quit()
        return 1
