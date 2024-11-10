"""Configuration settings for LoRa Chat application"""

# LoRa Radio Configuration
RADIO_FREQ = 915.0  # Frequency in MHz
CS_PIN = 5          # Chip select pin
RESET_PIN = 6       # Reset pin
BAUDRATE = 115200   # Serial baudrate

# Message Protocol
MAX_MESSAGE_LENGTH = 252  # Maximum message length for LoRa packet
RETRY_COUNT = 3          # Number of retries for failed transmissions
ACK_TIMEOUT = 2.0       # Timeout for acknowledgment in seconds

# Application Settings
NODE_ID = "PI_NODE_1"   # Unique identifier for this node
RECEIVE_TIMEOUT = 0.1   # Receive timeout in seconds
