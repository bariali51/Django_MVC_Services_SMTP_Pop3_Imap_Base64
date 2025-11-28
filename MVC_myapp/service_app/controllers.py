# service_app/controllers.py
from pathlib import Path

from .models import SMTPModel, POP3Model, IMAPModel, B64Model
from datetime import datetime

MAX_HISTORY = 20

# -----------------------------
# SMTP Controller
# -----------------------------
class SMTPController:
    def __init__(self):
        self.model = SMTPModel()

    def send_email(self, sender, pwd, receiver, subject, message, attachments=[]):
        return self.model.send_email(sender, pwd, receiver, subject, message, attachments)


class POP3Controller:
    def __init__(self):
        self.model = POP3Model()

    def login(self, email, password):
        return self.model.login(email, password)

    def fetch_emails(self):
        return self.model.fetch_emails()

    def get_message(self, index):
        return self.model.get_message(index)




# -------------------------------
# IMAP Controller
# -------------------------------
class IMAPController:
    def __init__(self):
        self.model = IMAPModel()

    def login(self, email, pwd):
        return self.model.login(email, pwd)

    def fetch_emails(self):
        return self.model.fetch_emails()

    def get_message(self, index):
        return self.model.get_message(index)



# -----------------------------
# Base64 Controller
# -----------------------------
class B64Controller:
    def __init__(self):
        self.model = B64Model()
        self.history = self.model.load_history()[-MAX_HISTORY:]

    # --- Text Methods ---
    def encode_text(self, text, urlsafe=False):
        if not text:
            return False, "No text provided"

        if urlsafe:
            success, result = self.model.urlsafe_encode_text(text)
            action = "urlsafe-encode-text"
        else:
            success, result = self.model.encode_text(text)
            action = "encode-text"

        if success:
            self._add_history(action, text, result)  # Record actual text/result for text ops
        return success, result

    def decode_text(self, text, urlsafe=False):
        if not text:
            return False, "No text provided"

        if urlsafe:
            success, result = self.model.urlsafe_decode_text(text)
            action = "urlsafe-decode-text"
        else:
            success, result = self.model.decode_text(text)
            action = "decode-text"

        if success:
            self._add_history(action, text, result)  # Record actual text/result for text ops
        return success, result

    # --- File Methods ('file_action' is the 'methods' part) ---
    def file_action(self, input_path, output_path, mode):
        if not input_path or not output_path:
            return False, "Input and Output files required!"

        input_path_obj = Path(input_path)
        if not input_path_obj.exists():
            return False, f"Input file not found: {input_path}"

        if mode == "encode":
            success, msg = self.model.encode_file(input_path, output_path)
            self._add_history("encode-file", input_path, output_path)
        elif mode == "decode":
            success, msg = self.model.decode_file(input_path, output_path)
            self._add_history("decode-file", input_path, output_path)
        else:
            success, msg = False, "Invalid file mode"

        return success, msg

    # --- History Methods ---
    def get_history(self):
        return self.history

    def _add_history(self, action, input_data, output_data):
        # input_data and output_data can be file paths or text strings
        entry = {
            "time": datetime.utcnow().isoformat() + "Z",
            "action": action,
            # Truncate text for history to avoid massive history file, keep file paths full
            "input": input_data if isinstance(input_data, Path) or not input_data else (input_data[:50] + "...") if len(
                input_data) > 50 else input_data,
            "output": output_data if isinstance(output_data, Path) or not output_data else (
                        output_data[:50] + "...") if len(output_data) > 50 else output_data
        }
        self.history.append(entry)
        self.history = self.history[-MAX_HISTORY:]
        self.model.save_history(self.history)