"""
Admin Panel Configuration
"""


class Config:
    """Centralized configuration for Admin Panel"""
    
    # API Configuration
    API_URL = "http://127.0.0.1:8000"
    UPLOAD_URL = f"{API_URL}/upload-image/"
    
    # Page Configuration
    APP_TITLE = "E-Ticaret Admin Paneli"
    PAGE_TITLE = "E-Ticaret Admin Paneli"
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    
    # Colors
    PRIMARY_COLOR = "#2196F3"
    SUCCESS_COLOR = "#4CAF50"
    ERROR_COLOR = "#F44336"
    WARNING_COLOR = "#FF9800"
    INFO_COLOR = "#2196F3"
    
    # Timeouts
    API_TIMEOUT = 5
    
    # Pagination
    ITEMS_PER_PAGE = 10


# Backward compatibility - expose as module-level variables
API_URL = Config.API_URL
UPLOAD_URL = Config.UPLOAD_URL
PAGE_TITLE = Config.PAGE_TITLE
WINDOW_WIDTH = Config.WINDOW_WIDTH
WINDOW_HEIGHT = Config.WINDOW_HEIGHT
PRIMARY_COLOR = Config.PRIMARY_COLOR
SUCCESS_COLOR = Config.SUCCESS_COLOR
ERROR_COLOR = Config.ERROR_COLOR
WARNING_COLOR = Config.WARNING_COLOR
INFO_COLOR = Config.INFO_COLOR
API_TIMEOUT = Config.API_TIMEOUT