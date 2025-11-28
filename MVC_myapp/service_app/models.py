import json
import smtplib
import imaplib
import base64
from email import encoders, parser
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import poplib
import email
from email.header import decode_header
from email import parser as email_parser
from datetime import datetime
# -------------------------------
# SMTP Model
# -------------------------------
class SMTPModel:
    @staticmethod
    def send_email(sender, pwd, receiver, subject, message, attachments=[]):
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receiver
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        for filepath, filename in attachments:
            with open(filepath, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
                encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={filename}")
            msg.attach(part)

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender, pwd)
            server.sendmail(sender, receiver, msg.as_string())
            server.quit()
            return True, "Email sent successfully"
        except Exception as e:
            return False, str(e)


class POP3Model:
    def __init__(self):
        self.conn = None
        self.emails_cache = []

    # تسجيل الدخول
    def login(self, email_addr, password):
        try:
            self.conn = poplib.POP3_SSL('pop.gmail.com', 995)
            self.conn.user(email_addr)
            self.conn.pass_(password)
            return True, "POP3 login successful"
        except Exception as e:
            return False, str(e)

    # جلب الرسائل الأخيرة
    def fetch_emails(self, limit=10):
        self.emails_cache = []
        if self.conn:
            try:
                resp, items, octets = self.conn.list()
                for i in items[-limit:]:
                    number = int(i.decode().split()[0])
                    resp, lines, octets = self.conn.retr(number)
                    msg_content = b'\n'.join(lines).decode('utf-8', errors='ignore')
                    msg_obj = parser.Parser().parsestr(msg_content)

                    subject = msg_obj['subject'] or '(No Subject)'
                    sender = msg_obj['from'] or 'Unknown Sender'
                    to = msg_obj['to'] or 'Unknown Recipient'
                    date = msg_obj['date'] or ''
                    body = ''

                    if msg_obj.is_multipart():
                        for part in msg_obj.walk():
                            if part.get_content_type() == 'text/plain':
                                body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    else:
                        body = msg_obj.get_payload(decode=True).decode('utf-8', errors='ignore')

                    snippet = body[:50] + ('...' if len(body) > 50 else '')

                    self.emails_cache.append({
                        'subject': subject,
                        'from': sender,
                        'to': to,
                        'date': date,
                        'body': body,
                        'snippet': snippet,
                        'read': False
                    })
                return True, self.emails_cache
            except Exception as e:
                return False, str(e)
        return False, "Not connected"

    # جلب رسالة محددة حسب index
    def get_message(self, index):
        try:
            return self.emails_cache[index]
        except IndexError:
            return {'subject': '', 'from': '', 'to': '', 'date': '', 'body': 'Message not found'}
# -------------------------------
# IMAP Model
# -------------------------------
class IMAPModel:
    def __init__(self):
        self.server = None
        self.conn = None
        self.emails_cache = []

    def login(self, email_addr, password):
        try:
            self.conn = imaplib.IMAP4_SSL('imap.gmail.com')
            self.conn.login(email_addr, password)
            self.conn.select('inbox')
            return True, "IMAP login successful"
        except Exception as e:
            return False, str(e)

    def fetch_emails(self, limit=10):
        self.emails_cache = []
        if self.conn:
            typ, data = self.conn.search(None, 'ALL')
            for num in data[0].split()[-limit:]:
                typ, msg_data = self.conn.fetch(num, '(RFC822)')
                raw = msg_data[0][1]
                msg_obj = email.message_from_bytes(raw)
                subject = msg_obj['subject'] or ''
                sender = msg_obj['from'] or ''
                body = ''
                if msg_obj.is_multipart():
                    for part in msg_obj.walk():
                        if part.get_content_type() == 'text/plain':
                            body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                else:
                    body = msg_obj.get_payload(decode=True).decode('utf-8', errors='ignore')
                self.emails_cache.append({'subject': subject, 'from': sender, 'body': body})
        return self.emails_cache

    def list_messages(self, limit=5):
        self.emails_cache = []
        if self.server:
            resp, items, octets = self.server.list()
            for i in items[-limit:]:
                resp, lines, octets = self.server.retr(int(i.split()[0]))
                msg_content = b'\n'.join(lines).decode('utf-8', errors='ignore')
                msg_obj = parser.Parser().parsestr(msg_content)
                subject = msg_obj['subject'] or '(No Subject)'
                sender = msg_obj['from'] or 'Unknown Sender'
                to = msg_obj['to'] or 'Unknown Recipient'
                date = msg_obj['date'] or ''
                body = ''
                if msg_obj.is_multipart():
                    for part in msg_obj.walk():
                        if part.get_content_type() == 'text/plain':
                            body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                else:
                    body = msg_obj.get_payload(decode=True).decode('utf-8', errors='ignore')
                self.emails_cache.append({
                    'subject': subject,
                    'from': sender,
                    'to': to,
                    'date': date,
                    'body': body,
                    'read': False
                })
        return self.emails_cache

    def get_message(self, index):
        try:
            return self.emails_cache[index]
        except IndexError:
            return {'subject': '', 'from': '', 'to': '', 'date': '', 'body': 'Message not found'}




# -------------------------------
# Base64 Model
# -------------------------------
MAX_HISTORY = 50
HISTORY_PATH = Path("b64_history.json")


class B64Model:
    # --- Existing File Methods ---
    @staticmethod
    def encode_file(input_path, output_path):
        try:
            with open(input_path, "rb") as f:
                data = f.read()
            # Use standard Base64 encode
            b64 = base64.b64encode(data).decode("ascii")
            with open(output_path, "w") as f:
                f.write(b64)
            return True, f"Encoded to {output_path}"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def decode_file(input_path, output_path):
        try:
            with open(input_path, "r") as f:
                raw = f.read()
            raw = raw.replace(" ", "").replace("\n", "").replace("\r", "").replace("\t", "")
            # Use standard Base64 decode
            decoded = base64.b64decode(raw, validate=True)
            with open(output_path, "wb") as f:
                f.write(decoded)
            return True, f"Decoded to {output_path}"
        except Exception as e:
            return False, str(e)

    # --- Existing Text Methods ---
    @staticmethod
    def encode_text(text):
        try:
            b64 = base64.b64encode(text.encode("utf-8")).decode("ascii")
            return True, b64
        except Exception as e:
            return False, str(e)

    @staticmethod
    def decode_text(text):
        try:
            text = text.replace(" ", "").replace("\n", "").replace("\r", "").replace("\t", "")
            decoded = base64.b64decode(text, validate=True)
            return True, decoded.decode("utf-8")
        except Exception as e:
            return False, str(e)

    # --- Optimizer/URL-Safe Methods (New) ---
    @staticmethod
    def urlsafe_encode_text(text):
        try:
            # URL-safe Base64 uses '-' instead of '+' and '_' instead of '/'
            b64_urlsafe = base64.urlsafe_b64encode(text.encode("utf-8")).decode("ascii").rstrip("=")
            return True, b64_urlsafe
        except Exception as e:
            return False, str(e)

    @staticmethod
    def urlsafe_decode_text(text):
        try:
            text = text.replace(" ", "").replace("\n", "").replace("\r", "").replace("\t", "")
            # Padding is often stripped from URL-safe variants, so we add it back before decoding
            padding = len(text) % 4
            if padding:
                text += "=" * (4 - padding)

            decoded = base64.urlsafe_b64decode(text, validate=True)
            return True, decoded.decode("utf-8")
        except Exception as e:
            return False, str(e)

    # --- History Methods (Existing) ---
    @staticmethod
    def save_history(history):
        try:
            with open(HISTORY_PATH, "w", encoding="utf-8") as f:
                json.dump(history[-MAX_HISTORY:], f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    @staticmethod
    def load_history():
        try:
            if HISTORY_PATH.exists():
                with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return []