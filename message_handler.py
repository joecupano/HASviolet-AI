"""Message handling and processing module"""

import time
import json
import psycopg2
import os
from datetime import datetime
from config import NODE_ID, MAX_MESSAGE_LENGTH

class MessageHandler:
    def __init__(self):
        self.message_queue = []
        self.received_messages = []
        self.last_message_id = 0
        self.db_conn = psycopg2.connect(os.environ['DATABASE_URL'])
        self.db_conn.autocommit = True
        self._load_last_message_id()
        self._load_recent_messages()

    def _load_last_message_id(self):
        """Load the last message ID from the database"""
        try:
            with self.db_conn.cursor() as cur:
                cur.execute("SELECT MAX(message_id) FROM messages")
                result = cur.fetchone()
                if result[0] is not None:
                    self.last_message_id = result[0]
        except Exception as e:
            print(f"Error loading last message ID: {str(e)}")

    def _load_recent_messages(self):
        """Load recent messages from the database"""
        try:
            with self.db_conn.cursor() as cur:
                cur.execute("""
                    SELECT message_id, node_id, content, timestamp, message_type 
                    FROM messages 
                    ORDER BY timestamp DESC 
                    LIMIT 100
                """)
                messages = cur.fetchall()
                for msg in reversed(messages):
                    self.received_messages.append({
                        'id': msg[0],
                        'node': msg[1],
                        'content': msg[2],
                        'timestamp': msg[3].isoformat(),
                        'type': msg[4]
                    })
        except Exception as e:
            print(f"Error loading recent messages: {str(e)}")

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
        try:
            with self.db_conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO messages (message_id, node_id, content, timestamp, message_type)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    message['id'],
                    message['node'],
                    message['content'],
                    datetime.fromisoformat(message['timestamp']),
                    message['type']
                ))
        except Exception as e:
            print(f"Error storing message in database: {str(e)}")

        self.received_messages.append(message)
        while len(self.received_messages) > 100:  # Keep last 100 messages in memory
            self.received_messages.pop(0)

    def get_received_messages(self):
        """Get all received messages"""
        return self.received_messages

    def cleanup(self):
        """Cleanup database connection"""
        if self.db_conn:
            self.db_conn.close()
