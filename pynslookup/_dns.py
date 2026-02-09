from enum import StrEnum


class RecordType(StrEnum):
    ANY = "ANY"
    A = "A"
    AAAA = "AAAA"
    TXT = "TXT"
    CNAME = "CNAME"
    MX = "MX"
    NS = "NS"
    PTR = "PTR"
    SOA = "SOA"


print(RecordType("M"))
