"""Message handling and processing module"""

import time
import json
from datetime import datetime
from config import NODE_ID, MAX_MESSAGE_LENGTH

class MessageHandler:
    def __init__(self):
        self.message_queue = []
        self.received_messages = []
        self.last_message_id = 0

    def format_message(self, content):
        """Format message with metadata"""
        self.last_message_id += 1
        message = {
            'id': self.last_message_id,
            'node': NODE_ID,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'type': 'message'
        }
        return json.dumps(message)

    def parse_message(self, message_data):
        """Parse received message"""
        try:
            message = json.loads(message_data)
            return True, message
        except json.JSONDecodeError:
            return False, None

    def queue_message(self, message):
        """Add message to sending queue"""
        if len(message) > MAX_MESSAGE_LENGTH:
            return False, "Message too long"
        
        formatted_message = self.format_message(message)
        if formatted_message is None:
            return False, "Message formatting failed"
            
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
