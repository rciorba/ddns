import re
import subprocess


def _assert(boolean):
    if not boolean:
        raise AssertionError("condition failed")


def _normalize(text):
    return text.strip().lower()


def _normalize_all(*args):
    return [_normalize(a) for a in args]


def validate_a(ip):
    parts = [int(x) for x in ip.split(".")]
    _assert(len(parts) == 4)


def validate_aaaa(ip):
    parts = [int(x, 16) for x in ip.split(":")]
    _assert(len(parts) == 8)


def validate_hostname(hostname, regex=re.compile('[a-z0-9_]+')):
    match = regex.match(hostname)
    _assert(match is not None)
    _assert(match.start() == 0)
    _assert(match.end() == len(hostname))


class Driver(object):
    shell_cmd = ['nsupdate', '-k', '/home/rciorba/repos/ddns_container/Kddns.+157+62662.private']
    update_cmd = '''
server 127.0.0.1 5053
zone ddns.ro
update delete {hostname}.ddns.ro.
update add {hostname}.ddns.ro. 600 A {ip}
send
'''
    @classmethod
    def update_a(cls, hostname, ip):
        hostname, ip = _normalize_all(hostname, ip)
        validate_a(ip)
        validate_hostname(hostname)
        sub = subprocess.Popen(
            cls.shell_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        update_cmd = cls.update_cmd.format(
            hostname=hostname,
            ip=ip)
        print update_cmd
        _out, _err = sub.communicate(update_cmd)  # waits for termination
        _assert(sub.returncode == 0)
        # import ipdb; ipdb.set_trace()
