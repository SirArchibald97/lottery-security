import logging


class SecurityFilter(logging.Filter):
    def filter(self, record):
        return "SECURITY" in record.getMessage()
