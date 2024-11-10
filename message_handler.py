"""Message handling and processing module"""

import time
import json
from datetime import datetime
from config import NODE_ID, MAX_MESSAGE_LENGTH, DEFAULT_CHANNEL, AVAILABLE_CHANNELS

class MessageHandler:
    def __init__(self):
        self.message_queue = []
        self.received_messages = []
        self.last_message_id = 0
        self.current_channel = DEFAULT_CHANNEL

    def set_channel(self, channel):
        """Set current channel"""
        if channel in AVAILABLE_CHANNELS:
            self.current_channel = channel
            return True, f"Switched to channel: {channel}"
        return False, f"Invalid channel. Available channels: {', '.join(AVAILABLE_CHANNELS)}"

    def get_current_channel(self):
        """Get current channel"""
        return self.current_channel

    def format_message(self, content):
        """Format message with metadata"""
        self.last_message_id += 1
        message = {
            'id': self.last_message_id,
            'node': NODE_ID,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'type': 'message',
            'channel': self.current_channel
        }
        return json.dumps(message)

    def parse_message(self, message_data):
        """Parse received message"""
        try:
            message = json.loads(message_data)
            # Ensure channel information exists, default to DEFAULT_CHANNEL if missing
            if 'channel' not in message:
                message['channel'] = DEFAULT_CHANNEL
            # Validate channel
            if message['channel'] not in AVAILABLE_CHANNELS:
                message['channel'] = DEFAULT_CHANNEL
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
        if 'channel' not in message:
            message['channel'] = DEFAULT_CHANNEL
        self.received_messages.append(message)
        while len(self.received_messages) > 100:  # Keep last 100 messages
            self.received_messages.pop(0)

    def get_received_messages(self, channel=None):
        """Get all received messages for a specific channel"""
        if channel is None:
            channel = self.current_channel
        return [msg for msg in self.received_messages if msg.get('channel', DEFAULT_CHANNEL) == channel]
