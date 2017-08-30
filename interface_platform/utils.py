# -*- coding: utf-8 -*-
import sys  # used to get commandline arguments
import re  # used for regular expressions


# 设置本地的HOST
# 由于Windows的hosts文件没有修改权限，无法验证
# TODO 到mac下验证该方法的正确性 11.23（首先将/etc/hosts文件的权限修改成777）
def set_host(hosts_dict):
    # key是hostname，value是ip地址
    for (key, value) in hosts_dict.items():
        if isValidHostname(key) and validIP(value) and exists(key) == False:
            update(value, key)
            return True
        else:
            return False


# 获取本地hosts路径
def get_hosts_path():
    if sys.platform.startswith("win"):
        return 'c:\windows\system32\drivers\etc\hosts'
    else:
        return '/etc/hosts'


def exists(hostname):
    """ str -> bool
    The exists function opens the host file and checks to see if the hostname requested exists in the host file.
    It opens the host file, reads the lines, and then a for loop checks each line to see if the hostname is in it.
    If it is, True is returned. If not, False is returned.
    :param hostname:
    :return:
    """
    filename = get_hosts_path()
    f = open(filename, 'r')
    hostfiledata = f.readlines()
    f.close()
    for item in hostfiledata:
        if hostname in item:
            return True
    return False


def update(ipaddress, hostname):
    """
    The update function takes the ip address and hostname passed into the function and adds it to the host file.
    :param ipaddress:
    :param hostname:
    """
    filename = get_hosts_path()
    outputfile = open(filename, 'a')
    entry = "\n" + ipaddress + "\t" + hostname + "\n"
    outputfile.writelines(entry)
    outputfile.close()


def validIP(ipaddress):
    """ str -> bool
    Found this on http://stackoverflow.com/questions/319279/how-to-validate-ip-address-in-python
    The function takes the IP address as a string and splits it by ".". It then checks to see if there are 4 items
    in the list. If not, it's not valid. Next, it makes sure the last two characters are not ".0", which would signify an
    invalid address. Third it checks the last character to make sure it's not a ".", which would be invalid. Lastly, it
    checks each item to make sure it's greater than 0 or equal to zero but less than or equal to 255.
    :param ipaddress:
    :return:
    """
    parts = ipaddress.split(".")
    if len(parts) != 4:
        return False
    if ipaddress[-2:] == '.0': return False
    if ipaddress[-1] == '.': return False
    for item in parts:
        if not 0 <= int(item) <= 255:
            return False
    return True


def isValidHostname(hostname):
    """ str -> bool
    Found this on from http://stackoverflow.com/questions/2532053/validate-a-hostname-string
    First it checks to see if the hostname is too long. Next, it checks to see if the first character is a number.
    If the last character is a ".", it is removed. A list of acceptable characters is then compiled and each section
    of the host name, split by any ".", is checked for valid characters. If there everything is valid, True is returned.
    :param hostname:
    :return:
    """
    if len(hostname) > 255:
        return False
    if hostname[0].isdigit(): return False
    if hostname[-1:] == ".":
        hostname = hostname[:-1]  # strip exactly one dot from the right, if present
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))


if __name__ == "__main__":
    set_host({"super.qiye.yixin.im":"106.2.124.114"})
    print exists("super.qiye.yixin.im")
    # update("1.1.1.1", "aaa.com")
