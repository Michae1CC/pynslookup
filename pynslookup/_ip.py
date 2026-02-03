def is_ip_address(value: str) -> bool:
    import ipaddress

    try:
        ipaddress.ip_address(value)
    except ValueError:
        return False

    return True
