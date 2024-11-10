"""LoRa Radio Management Module with Simulation Support"""

import time
import random
import json
from config import *
from message_handler import MessageHandler, SHARED_KEY

class LoRaRadio:
    def __init__(self):
        self.is_initialized = False
        self.simulation_mode = True  # For prototype testing without hardware
        self.last_received = time.time()
        self.message_handler = MessageHandler()  # For encryption in simulation
        
    def initialize(self):
        """Initialize LoRa radio hardware or simulation"""
        try:
            if self.simulation_mode:
                print("Starting in simulation mode")
                self.is_initialized = True
                return True
            else:
                # Real hardware initialization code here
                # (Kept for future hardware implementation)
                return False
        except Exception as e:
            print(f"Radio initialization failed: {str(e)}")
            return False

    def send_message(self, message):
        """Send a message via LoRa radio (simulated in prototype)"""
        if not self.is_initialized:
            return False, "Radio not initialized"
            
        try:
            if self.simulation_mode:
                print(f"Simulated sending: {message}")
                return True, "Message sent successfully"
            return False, "Hardware mode not implemented"
        except Exception as e:
            return False, f"Send failed: {str(e)}"

    def receive_message(self):
        """Receive a message from LoRa radio (simulated in prototype)"""
        if not self.is_initialized:
            return False, None, "Radio not initialized"
            
        try:
            if self.simulation_mode:
                current_time = time.time()
                # Simulate occasional message reception
                if current_time - self.last_received > 10 and random.random() < 0.1:
                    self.last_received = current_time
                    content = f"Test message {random.randint(1, 100)}"
                    encrypted_content = self.message_handler.encrypt_content(content)
                    simulated_message = {
                        'id': random.randint(1000, 9999),
                        'node': f"SIM_NODE_{random.randint(1,5)}",
                        'content': encrypted_content,
                        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
                        'type': 'message',
                        'encrypted': True
                    }
                    return True, json.dumps(simulated_message), "Message received"
                return True, None, "No message"
            return False, None, "Hardware mode not implemented"
        except Exception as e:
            return False, None, f"Receive failed: {str(e)}"

    def cleanup(self):
        """Cleanup radio resources"""
        self.is_initialized = False
