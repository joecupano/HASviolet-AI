"""Message handling and processing module with encryption support"""

import time
import json
from datetime import datetime
from config import NODE_ID, MAX_MESSAGE_LENGTH
from cryptography.fernet import Fernet
import base64

# Shared encryption key for all instances
# In a production environment, this should be securely distributed
SHARED_KEY = Fernet.generate_key()

class MessageHandler:
    def __init__(self):
        self.message_queue = []
        self.received_messages = []
        self.last_message_id = 0
        self._init_encryption()
    
    def _init_encryption(self):
        """Initialize encryption using shared key"""
        self.cipher_suite = Fernet(SHARED_KEY)

    def encrypt_content(self, content):
        """Encrypt message content"""
        try:
            if isinstance(content, str):
                content_bytes = content.encode()
            else:
                content_bytes = str(content).encode()
            encrypted_content = self.cipher_suite.encrypt(content_bytes)
            return base64.b64encode(encrypted_content).decode('utf-8')
        except Exception as e:
            print(f"Encryption error: {str(e)}")
            return None

    def decrypt_content(self, encrypted_content):
        """Decrypt message content"""
        try:
            encrypted_bytes = base64.b64decode(encrypted_content.encode('utf-8'))
            decrypted_content = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted_content.decode('utf-8')
        except Exception as e:
            print(f"Decryption error: {str(e)}")
            return None

    def format_message(self, content):
        """Format message with metadata and encryption"""
        self.last_message_id += 1
        encrypted_content = self.encrypt_content(content)
        if encrypted_content is None:
            return None
            
        message = {
            'id': self.last_message_id,
            'node': NODE_ID,
            'content': encrypted_content,
            'timestamp': datetime.now().isoformat(),
            'type': 'message',
            'encrypted': True
        }
        return json.dumps(message)

    def parse_message(self, message_data):
        """Parse and decrypt received message"""
        try:
            message = json.loads(message_data)
            if message.get('encrypted', False):
                decrypted_content = self.decrypt_content(message['content'])
                if decrypted_content is not None:
                    message['content'] = decrypted_content
                else:
                    return False, None
            return True, message
        except json.JSONDecodeError:
            return False, None

    def queue_message(self, message):
        """Add message to sending queue"""
        if len(message) > MAX_MESSAGE_LENGTH:
            return False, "Message too long"
        
        formatted_message = self.format_message(message)
        if formatted_message is None:
            return False, "Message encryption failed"
            
        self.message_queue.append(formatted_message)
        return True, "Message queued"

    def get_next_message(self):
        """Get next message from queue"""
        if not self.message_queue:
            return None
        return self.message_queue.pop(0)

    def store_received_message(self, message):
        """Store received message"""
        self.received_messages.append(message)
        while len(self.received_messages) > 100:  # Keep last 100 messages
            self.received_messages.pop(0)

    def get_received_messages(self):
        """Get all received messages"""
        return self.received_messages
