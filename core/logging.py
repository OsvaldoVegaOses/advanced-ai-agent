"""
Core Logging Module
Centralized logging configuration for the Advanced AI Agent
"""

import logging
import sys
from typing import Any, Dict
from datetime import datetime


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance"""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # Configure handler
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger


class PerformanceLogger:
    """Simple performance logger"""
    
    def __init__(self):
        self.logger = get_logger("performance")
    
    def log_model_inference(self, model_name: str, operation: str, 
                          input_tokens: int, output_tokens: int,
                          processing_time: float, cost: float):
        """Log model inference performance"""
        self.logger.info(
            f"Model: {model_name}, Operation: {operation}, "
            f"Tokens: {input_tokens}+{output_tokens}, "
            f"Time: {processing_time:.3f}s, Cost: ${cost:.6f}"
        )


# Global instance
performance_logger = PerformanceLogger()