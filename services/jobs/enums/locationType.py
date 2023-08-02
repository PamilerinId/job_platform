import enum

class LocationType(str, enum.Enum):
    OFFICE = 'OFFICE'
    REMOTE = 'REMOTE'
    HYBRID = 'HYBRID'