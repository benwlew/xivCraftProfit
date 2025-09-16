import logging

def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:    
    """Configure and return a logger instance.
    
    Args:
        name: Name of the logger, typically __name__
        level: Logging level, defaults to INFO
        
    Returns:
        Configured logger instance
    """
    # Configure logging only if it hasn't been configured yet
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    return logging.getLogger(name)
    