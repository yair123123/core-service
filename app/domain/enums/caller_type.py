from enum import StrEnum


class CallerType(StrEnum):
    CUSTOMER = "CUSTOMER"
    DRIVER = "DRIVER"
    UNKNOWN = "UNKNOWN"
