import logging
import os
from datetime import datetime

class Logger:
    def __init__(self, log_file='logs/deadlock_detection.log'):
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        self.logger = logging.getLogger('DeadlockDetection')
        self.logger.setLevel(logging.DEBUG)
        
        if not self.logger.handlers:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def log(self, message, level='info'):
        if level == 'debug':
            self.logger.debug(message)
        elif level == 'info':
            self.logger.info(message)
        elif level == 'warning':
            self.logger.warning(message)
        elif level == 'error':
            self.logger.error(message)
        elif level == 'critical':
            self.logger.critical(message)
        else:
            self.logger.info(message)
    
    def log_error(self, message, exception=None):
        if exception:
            self.logger.error(f"{message}: {str(exception)}", exc_info=True)
        else:
            self.logger.error(message)
    
    def log_detection_start(self, system_info):
        self.logger.info("="*50)
        self.logger.info("Starting Deadlock Detection")
        self.logger.info(f"System Info: {system_info}")
        self.logger.info("="*50)
    
    def log_detection_end(self, result):
        self.logger.info("="*50)
        self.logger.info(f"Detection Complete: Deadlock={result.get('deadlock', False)}")
        self.logger.info("="*50)
