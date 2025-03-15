import os
import click
import smtplib
import mimetypes
from email.message import EmailMessage
from mtb.utils import config_parser
from mtb.utils.decorators import log_header_footer

@click.command(name="send-email", help="Send an email with optional attachments and priority.")
@click.option('-s', '--subject', required=True, help="Email subject")
@click.option('-f', '--from', 'from_addr', default=None, help="Sender email address (if not provided, defaults from config)")
@click.option('-t', '--to', required=True, multiple=True, help="Recipient email address (can be used multiple times)")
@click.option('-c', '--cc', multiple=True, help="CC recipient email address (can be used multiple times)")
@click.option('-C', '--cco', multiple=True, help="BCC recipient email address (can be used multiple times)")
@click.option('-m', '--message', required=True, help="Email message as a string or a path to a file containing the message")
@click.option('-F', '--format', 'msg_format', type=click.Choice(['text', 'html'], case_sensitive=False),
              default="text", help="Email message format: text or html")
@click.option('-a', '--attachment', 'attachments', multiple=True, type=click.Path(exists=True),
              help="File(s) to attach (can be used multiple times)")
@click.option('-p', '--priority', default="3", help="Email priority (1=High, 3=Normal, 5=Low)")
@log_header_footer
def send_email(subject, from_addr, to, cc, cco, message, msg_format, attachments, priority):
    """
    Send an email with the provided parameters.

    The SMTP server, port, and default sender address are read from the global configuration (config.yaml).
    """
    # Load global configuration.
    config = config_parser.load_config("config.yaml")
    email_server = config.get("email_server", "localhost")
    email_port = config.get("email_port", 25)
    if from_addr is None:
        from_addr = config.get("email_from", "noreply@example.com")

    # Create the EmailMessage object.
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = ', '.join(to)
    if cc:
        msg['Cc'] = ', '.join(cc)
    # BCC is not added to headers.
    msg['X-Priority'] = priority  # Standard header for email priority.
    if priority == "1":
        msg['Importance'] = 'high'
    elif priority == "5":
        msg['Importance'] = 'low'
    else:
        msg['Importance'] = 'normal'
    
    # Determine if message parameter is a file path or direct text.
    if os.path.exists(message):
        with open(message, 'r') as f:
            msg_content = f.read()
    else:
        msg_content = message

    # Add content in the requested format.
    if msg_format.lower() == "html":
        msg.add_alternative(msg_content, subtype="html")
    else:
        msg.set_content(msg_content)

    # Attach files if provided.
    for file_path in attachments:
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            mime_type = 'application/octet-stream'
        main_type, sub_type = mime_type.split('/', 1)
        with open(file_path, 'rb') as f:
            file_data = f.read()
        msg.add_attachment(file_data, maintype=main_type, subtype=sub_type, filename=os.path.basename(file_path))

    # Combine all recipient addresses (to, cc, bcc) for sending.
    recipients = list(to) + list(cc) + list(cco)

    # Send the email using the SMTP server and port from configuration.
    try:
        with smtplib.SMTP(email_server, email_port) as server:
            server.send_message(msg, from_addr=from_addr, to_addrs=recipients)
        click.echo("Email sent successfully.")
    except Exception as e:
        click.echo(f"Failed to send email: {e}", err=True)

if __name__ == '__main__':
    send_email()
