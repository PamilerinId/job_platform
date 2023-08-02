import enum


class Qualification(str, enum.Enum): #refactor
    NONE = 'NONE'
    BACHELORS = 'BACHELORS'
    OND = 'OND'
    HND = 'HND'
    NCE = 'NCE'
    MASTERS = 'MASTERS'
    DOCTORAL = 'DOCTORAL'
    PHD = 'PHD'
    OTHER = 'OTHER'