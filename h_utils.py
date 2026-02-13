"""
contains code that make my life a bit easier
"""
import ipaddress
import csv
import re
from itertools import product
from typing import Iterable, Optional, Callable, Dict, Generator

def ip_in_range(ip: ipaddress.IPv4Address | ipaddress.IPv6Address | str, 
                range: ipaddress.IPv4Network | ipaddress.IPv6Network | str) -> bool | None:
    """
    Compares an ip address to a range and determines if ip is in range.

    Accepts both IPv4 and IPv6.

    Returns None if the types of ip and range do not match.
    
    :param ip: ip address
    :type ip: ipaddress.IPv4Address | ipaddress.IPv6Address | str
    :param range: ip range to compare ip to
    :type range: ipaddress.IPv4Network | ipaddress.IPv6Network | str
    :return: returns true if ip in range, false if ip not in range, and none if types don't match
    :rtype: bool | None
    """
    if isinstance(ip, str):
        ip = ip_version(ip)
        if ip.prefixlen == 32:
            ip = ip[0]
    if isinstance(range, str):
        range = ip_version(range)

    ip_addr_func = None
    if (isinstance(ip, ipaddress.IPv4Address) and isinstance(range, ipaddress.IPv4Network)):
        ip_addr_func = ipaddress.IPv4Address
    if (isinstance(ip, ipaddress.IPv6Address) and isinstance(range, ipaddress.IPv6Network)):
        ip_addr_func = ipaddress.IPv6Address
    if ip_addr_func is None:
        return None
    ip_network = ip_addr_func(int(ip) & int(range.netmask))
    if ip_network == range.network_address:
        return True
    return False

def ip_version(ip: str) -> ipaddress.IPv4Network | ipaddress.IPv6Network | None:
    """
    detects the ip version of the given string
    
    :param ip: ip in string format. can be with or without prefix
    :type ip: str
    :return: returns either IPv4Network or IPv6Network for valid IP Addresses or Networks. 
    Returns None if neither are true.
    :rtype: ipaddress.IPv4Network | ipaddress.IPv6Network | None
    """
    try: return ipaddress.IPv4Network(ip)
    except:
        try: return ipaddress.IPv6Network(ip)
        except: pass
    return None

def open_csv(filename: str, header: bool = True) -> list:
    """
    Open csv and return data.
        
    :param filename: filename to open
    :type filename: str
    :param header: Set to True if the CSV file has headers for each column. Set to False otherwise. Assumed to be True by default.
    :type header: bool
    :return: Return the data from the CSV as a list.
    :rtype: list
    """
    with open(filename) as f:
        if header:
            reader = csv.DictReader(f)
        else:
            reader = csv.reader(f)
        return [line for line in reader]

def write_csv(data: list, filename: str, fieldnames: bool = None) -> None:
    with open(filename, "w", newline = "") as f:
        if fieldnames is not None:
            writer = csv.DictWriter(f, fieldnames = fieldnames)
            writer.writeheader()
        else:
            writer = csv.writer(f)

        writer.writerows(data)

def get_input(name: str, return_iterable: Iterable = False, prompt: Optional[str | None] = None, help: str = "invalid input", check_function: Callable = None) -> Dict:
    """
    Can be used for interactive input.
    Gets input from the user and will validate that against the callable check_function.

    The user can be asked for multiple values if the return_iterable variable is True.

    If the user enters in invalid data (result of check_function(input) == False) then the user will be asked again for input.
    
    :param name: Name to display to the end user
    :param check_function: Callable that is used to check if the input is valid. If the input from the user returns true from this function, it will be returned.
                            If this returns false, the user will be asked again for input.
    :param return_iterable: by default, the return value is a single str. If this is true, the user is asked multiple times
    :param prompt: Prompt to display to user when asking for input
    :param help: message to display to user when their given input fails the check_function
    """
    return_dict = dict()

    if return_iterable:
        temp = set()
    else:
        temp = None

    if prompt is None:
        prompt = f"{name}: "

    while user_input := input(prompt):
        if check_function is not None and check_function(user_input):
            if return_iterable:
                temp.add(user_input)
            else:
                temp = user_input
                break
        else:
            print(help)
        if check_function is None:
            if return_iterable:
                temp.add(user_input)
            else:
                temp = user_input
                break
        
    return_dict.update({name : temp})

    return return_dict

def expand_tn(tn: str) -> Generator:
    """
    Expands a telephone number pattern from Cisco Call Manager and returns a generator of all possible numbers.

    Example Patterns
    1316555101[0-9]
    131655510XX
    131655511[0-2]X
    1316555111X[4-8]

    1316555101[0-9] will return a generator containing
    13165551010, 13165551011, 13165551012, 13165551013, ... 13165551019

    :param tn: telephone number pattern to expand
    :type tn: str

    :return generator
    """
    FULL_NUMBER_RE = r"\[([0-9])-([0-9])\]|(X)|([0-9])"
    ranges = []
    for match in re.finditer(FULL_NUMBER_RE, tn):
        match_groups = match.groups()
        m = [m for m in match_groups if m is not None]
        if len(m) == 1:
            if m[0] == "X":
                start = 0
                stop = 10
            else:
                start = int(m[0])
                stop = start + 1
        else:
            start = int(m[0])
            stop = int(m[1]) + 1
        ranges.append(list(range(start, stop)))

    for x in product(*ranges):
        single_expanded_number = ""
        for xx in x:
            single_expanded_number += f"{xx}"
        yield single_expanded_number

if __name__ == "__main__":
    pass