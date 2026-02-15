from enum import StrEnum


class RecordType(StrEnum):
    A = "A"
    AAAA = "AAAA"
    TXT = "TXT"
    CNAME = "CNAME"
    MX = "MX"
    NS = "NS"
    SOA = "SOA"
