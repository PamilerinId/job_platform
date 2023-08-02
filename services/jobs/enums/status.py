import enum

class JobStatus(str, enum.Enum):
    DRAFT = 'DRAFT'
    ACTIVE = 'ACTIVE'
    PAUSED = 'PAUSED'
    CLOSED = 'CLOSED'


class ApplicationStatus(str, enum.Enum):
    PENDING = 'PENDING'
    SHORTLISTED = "SHORTLISTED"
    INTERVIEWING = "INTERVIEWING"
    HIRED = 'HIRED'
    REJECTED = 'REJECTED'
