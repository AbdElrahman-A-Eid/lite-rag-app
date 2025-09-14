"""
Base controllers for handling common operations.
"""

import logging

from config import Settings


class BaseController:
    """
    Base controller for handling common operations.
    """

    def __init__(self, settings: Settings):
        """
        Initialize the base controller.
        """
        self.settings = settings
        self.logger = logging.getLogger(self.__class__.__name__)
