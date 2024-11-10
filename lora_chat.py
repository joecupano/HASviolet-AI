"""Main LoRa Chat Application"""

import threading
import time
import sys
from radio_manager import LoRaRadio
from message_handler import MessageHandler
from user_interface import ChatInterface
from config import *

class LoRaChat:
    def __init__(self):
        self.radio = LoRaRadio()
        self.message_handler = MessageHandler()
        self.interface = ChatInterface()
        self.running = False

    def initialize(self):
        """Initialize the chat application"""
        if not self.radio.initialize():
            print("Failed to initialize radio. Exiting.")
            return False
        return True

    def receive_loop(self):
        """Message receiving loop"""
        while self.running:
            success, message, status = self.radio.receive_message()
            if success and message:
                success, parsed_message = self.message_handler.parse_message(message)
                if success:
                    self.message_handler.store_received_message(parsed_message)
                    self.interface.update_messages(parsed_message)
            time.sleep(0.1)

    def send_loop(self):
        """Message sending loop"""
        while self.running:
            message = self.message_handler.get_next_message()
            if message:
                success, status = self.radio.send_message(message)
                if not success:
                    # Requeue failed messages
                    self.message_handler.queue_message(message)
            time.sleep(0.1)

    def process_command(self, command):
        """Process special commands"""
        if command.startswith("/"):
            parts = command.split()
            cmd = parts[0].lower()
            
            if cmd == "/quit":
                self.stop()
                return True
            elif cmd == "/status":
                status_msg = {
                    'node': NODE_ID,
                    'content': f"Radio Status: {'Connected' if self.radio.is_initialized else 'Disconnected'}",
                    'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
                    'type': 'status',
                    'channel': self.message_handler.get_current_channel()
                }
                self.interface.update_messages(status_msg)
                return True
            elif cmd == "/channel" and len(parts) > 1:
                channel = parts[1].lower()
                success, message = self.message_handler.set_channel(channel)
                if success:
                    self.interface.set_channel(channel)
                status_msg = {
                    'node': 'System',
                    'content': message,
                    'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
                    'type': 'status',
                    'channel': self.message_handler.get_current_channel()
                }
                self.interface.update_messages(status_msg)
                return True
            elif cmd == "/channels":
                channels_msg = {
                    'node': 'System',
                    'content': f"Available channels: {', '.join(AVAILABLE_CHANNELS)}",
                    'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
                    'type': 'status',
                    'channel': self.message_handler.get_current_channel()
                }
                self.interface.update_messages(channels_msg)
                return True
        return False

    def run(self):
        """Run the chat application"""
        if not self.initialize():
            return

        self.running = True
        self.interface.start()

        # Start receiver and sender threads
        receive_thread = threading.Thread(target=self.receive_loop)
        send_thread = threading.Thread(target=self.send_loop)
        receive_thread.start()
        send_thread.start()

        try:
            while self.running:
                user_input = self.interface.get_input()
                if user_input:
                    if not self.process_command(user_input):
                        success, status = self.message_handler.queue_message(user_input)
                        if not success:
                            self.interface.update_messages({
                                'node': 'System',
                                'content': f"Error: {status}",
                                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
                                'type': 'error',
                                'channel': self.message_handler.get_current_channel()
                            })

        except KeyboardInterrupt:
            self.stop()

        receive_thread.join()
        send_thread.join()

    def stop(self):
        """Stop the chat application"""
        self.running = False
        self.interface.stop()
        self.radio.cleanup()

if __name__ == "__main__":
    chat = LoRaChat()
    chat.run()
