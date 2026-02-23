from __future__ import annotations

import argparse
import socket
import sys
import struct
import random

from collections.abc import Sequence

from typing import cast
from typing import Mapping

from .const import PROGRAM_NAME

from ._dns import RecordType
from .util.bijective_dict import BijectiveDict

_RECORD_TYPE_TO_ID_MAP: BijectiveDict[RecordType, int] = BijectiveDict(
    {
        RecordType("A"): 1,
        RecordType("AAAA"): 28,
        RecordType("TXT"): 28,
        RecordType("CNAME"): 5,
        RecordType("MX"): 15,
        RecordType("NS"): 2,
        RecordType("SOA"): 6,
    }
)


def _record_type_to_id(record_type: RecordType) -> int:
    try:
        return _RECORD_TYPE_TO_ID_MAP[record_type]
    except KeyError:
        raise ValueError(f"No record id set for record type {record_type}")


def _record_id_to_type(id: int) -> RecordType:
    try:
        return _RECORD_TYPE_TO_ID_MAP.inv[id]
    except KeyError:
        raise ValueError(f"No record type set for record id {id}")


# https://datatracker.ietf.org/doc/rfc1035/
# https://datatracker.ietf.org/doc/rfc2136/


def parse_name(message: bytes, offset: int) -> tuple[str, int]:
    """
    Parse domain name (handles DNS compression).
    Returns (name, new_offset)
    """
    labels = []
    jumped = False
    original_offset = offset

    while True:
        length = message[offset]

        # Check for compression (first two bits = 11)
        if (length & 0xC0) == 0xC0:
            pointer = struct.unpack("!H", message[offset : offset + 2])[0]
            pointer &= 0x3FFF
            offset = pointer
            if not jumped:
                original_offset += 2
            jumped = True
            continue

        if length == 0:
            offset += 1
            break

        offset += 1
        labels.append(message[offset : offset + length].decode())
        offset += length

    name = ".".join(labels)

    if jumped:
        return name, original_offset
    return name, offset


def _parse_dns_response(data: bytes) -> None:
    header = struct.unpack("!HHHHHH", data[:12])
    tid, flags, qdcount, ancount, nscount, arcount = header

    print("Transaction ID:", hex(tid))
    print("Flags:", hex(flags))
    print("Questions:", qdcount)
    print("Answers:", ancount)

    offset = 12

    # ---- Parse Question Section ----
    for _ in range(qdcount):
        qname, offset = parse_name(data, offset)
        qtype, qclass = struct.unpack("!HH", data[offset : offset + 4])
        offset += 4
        print("\nQuestion:")
        print("  Name:", qname)
        print("  Type:", qtype)
        print("  Class:", qclass)

    # ---- Parse Answer Section ----
    for i in range(ancount):
        name, offset = parse_name(data, offset)
        rid, rclass, ttl, rdlength = struct.unpack("!HHIH", data[offset : offset + 10])
        offset += 10

        rdata = data[offset : offset + rdlength]
        offset += rdlength

        print(f"\nAnswer {i+1}:")
        print("  Name:", name)
        print("  Type:", _record_type_to_id(rid))
        print("  Class:", rclass)
        print("  TTL:", ttl)

        # Handle A record
        if rid == 1 and rdlength == 4:
            ip = socket.inet_ntoa(rdata)
            print("  Address:", ip)
        else:
            print("  Raw Data:", rdata)


def _create_dns_query_message(*, domain: str, q_type: RecordType) -> bytes:
    transaction_id = random.randint(0, 65535)  # 16-bit ID
    flags = 0x0100  # Standard query with Recursion Desired
    qdcount = 1  # One question
    ancount = 0
    nscount = 0
    arcount = 0

    # Pack header (network byte order = big endian)
    header = struct.pack(
        "!HHHHHH", transaction_id, flags, qdcount, ancount, nscount, arcount
    )

    qname = b""
    for label in domain.split("."):
        qname += struct.pack("B", len(label))
        qname += label.encode()
    qname += b"\x00"

    q_class = 1  # Class IN (Internet)
    _q_type = 1

    question = qname + struct.pack("!HH", _q_type, q_class)

    return header + question


def _run(args: argparse.Namespace) -> int:

    # TODO: This can be a list of record types
    record_type_raw: str = args._type
    port: int = args.port
    recurse: bool = args.recurse

    if not (0 <= port <= 65_535):
        print("*** Invalid option: port", file=sys.stderr)
        return 1

    record_type: RecordType = RecordType("A")

    try:
        record_type = RecordType((cast(str, args._type)).upper())
    except ValueError:
        print("*** Invalid option: type", file=sys.stderr)
        # Continue on with the default record type

    dns_query_message = _create_dns_query_message(
        domain="google.com", q_type=RecordType("A")
    )

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(dns_query_message, ("192.168.2.1", 53))
        data, response_server_address = sock.recvfrom(512)
        _parse_dns_response(data)

    return 0


def main(argv: Sequence[str] | None = None) -> int:

    argv = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(prog=PROGRAM_NAME)

    parser.add_argument(
        "-type",
        type=str,
        help=(f"Changes the resource record type for the query."),
        default=f"A",
        metavar="type",
        dest="_type",
    )

    parser.add_argument(
        "-port",
        type=int,
        help=(
            f"Changes the default TCP/UDP DNS name server port to the value specified."
        ),
        default=50,
        metavar="port",
        dest="port",
    )

    parser.add_argument(
        "-recurse",
        type=bool,
        help=(
            f"Tells the DNS name server to query other servers if it doesn't have the information."
        ),
        default=False,
        metavar="recurse",
        dest="recurse",
    )

    args = parser.parse_args()

    return _run(args)
