import enum

class LocationType(str, enum.Enum):
    ONSITE = 'ONSITE'
    REMOTE = 'REMOTE'
    HYBRID = 'HYBRID'