import os
import subprocess
import sys
from configparser import ConfigParser

def install_packages():
    """Install required packages."""
    packages = [
        'sqlalchemy',
        'argparse',
        'pyzbar',
        'opencv-python',
        'pillow',
        'argon2-cffi',
        'requests',
        'python-barcode'
    ]
    subprocess.check_call([sys.executable, "-m", "pip", "install", *packages])

def create_config_file():
    """Create a config.ini file."""
    config = ConfigParser()

    config['database'] = {
        'db_file': 'inventory_management.db'
    }
    
    config['logging'] = {
        'log_file': 'inventory_management.log',
        'log_level': 'INFO'
    }

    with open('config.ini', 'w') as configfile:
        config.write(configfile)

def create_directories():
    """Create necessary directories."""
    os.makedirs('barcodes', exist_ok=True)
    os.makedirs('scanned_barcodes', exist_ok=True)

def initialize_database():
    """Initialize the database."""
    from database import DatabaseManager
    db_manager = DatabaseManager('inventory_management.db')
    print("Database initialized.")

def main():
    print("Installing required packages...")
    install_packages()
    
    print("Creating configuration file...")
    create_config_file()

    print("Creating necessary directories...")
    create_directories()
    
    print("Initializing database...")
    initialize_database()
    
    print("Setup complete. You can now run the application.")

if __name__ == "__main__":
    main()
