import imaplib
import email

# Configuration
EMAIL_ADDRESS = 'bryanjorge417@gmail.com'  # Your Email Address
EMAIL_PASSWORD = 'Not My pass'             # Your Email Password/App Password
IMAP_SERVER = 'imap.gmail.com'             #imap for your email provider

def connect_to_email():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    return mail


def safe_decode(payload, charset):
    """
    Safely decode email bodies without crashing on invalid bytes.
    """
    if not payload:
        return ""

    # Try declared charset first
    if charset:
        try:
            return payload.decode(charset, errors="ignore")
        except:
            pass

    # Try UTF-8
    try:
        return payload.decode("utf-8", errors="ignore")
    except:
        pass

    # Final fallback: Latin-1 (always works)
    return payload.decode("latin-1", errors="ignore")


def fetch_emails(mail):
    mail.select("inbox")
    _, data = mail.search(None, "UNSEEN")

    email_ids = data[0].split()
    emails = []

    for email_id in email_ids:
        _, msg_data = mail.fetch(email_id, "(BODY.PEEK[])") #use PEEK to avoid marking the email as read
        msg = email.message_from_bytes(msg_data[0][1])

        email_info = {
            'id': email_id,          # Needed by main.py
            'from': msg['From'],
            'subject': msg['Subject'],
            'body': ""
        }

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload(decode=True)
                    charset = part.get_content_charset()
                    email_info['body'] = safe_decode(payload, charset)
                    break
        else:
            payload = msg.get_payload(decode=True)
            charset = msg.get_content_charset()
            email_info['body'] = safe_decode(payload, charset)
