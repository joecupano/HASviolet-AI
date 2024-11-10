"""Console-based user interface for LoRa Chat"""

import os
import sys
import threading
import time
from config import NODE_ID, DEFAULT_CHANNEL, AVAILABLE_CHANNELS

class ChatInterface:
    def __init__(self):
        self.running = False
        self.input_buffer = ""
        self.messages = []
        self.lock = threading.Lock()
        self.current_channel = DEFAULT_CHANNEL

    def clear_screen(self):
        """Clear the console screen"""
        os.system('clear' if os.name == 'posix' else 'cls')

    def print_header(self):
        """Print chat interface header"""
        print("=" * 50)
        print(f"LoRa Chat - Node ID: {NODE_ID} - Channel: {self.current_channel}")
        print("=" * 50)
        print("Commands: /quit to exit, /status for radio status")
        print("/channel <name> to switch channels, /channels to list channels")
        print("-" * 50)

    def print_messages(self):
        """Print message history"""
        with self.lock:
            self.clear_screen()
            self.print_header()
            
            # Filter messages for current channel
            channel_messages = [msg for msg in self.messages[-10:] 
                              if isinstance(msg, dict) and 
                              msg.get('channel', DEFAULT_CHANNEL) == self.current_channel]
            
            for msg in channel_messages:
                timestamp = msg.get('timestamp', '').split('T')[1][:8]
                node = msg.get('node', 'Unknown')
                content = msg.get('content', '')
                print(f"[{timestamp}] {node}: {content}")
            
            print("\n" + "-" * 50)
            print("Enter message:", self.input_buffer, end='', flush=True)

    def set_channel(self, channel):
        """Set current channel"""
        if channel in AVAILABLE_CHANNELS:
            self.current_channel = channel
            return True
        return False

    def update_messages(self, message):
        """Update message display"""
        with self.lock:
            self.messages.append(message)
            self.print_messages()

    def get_input(self):
        """Get user input"""
        while self.running:
            try:
                char = sys.stdin.read(1)
                if char == '\n':
                    with self.lock:
                        message = self.input_buffer
                        self.input_buffer = ""
                        self.print_messages()
                        return message
                elif char == '\x7f':  # Backspace
                    self.input_buffer = self.input_buffer[:-1]
                else:
                    self.input_buffer += char
                self.print_messages()
            except Exception:
                continue
        return None

    def start(self):
        """Start the interface"""
        self.running = True
        self.clear_screen()
        self.print_messages()

    def stop(self):
        """Stop the interface"""
        self.running = False
