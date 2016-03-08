import base64
import re
import string
from random import sample
from netaddr import IPAddress, IPRange, IPNetwork, AddrFormatError

def get_targets(target):

    targets = []

    if '-' in target:
        ip_range = target.split('-')
        try:
            hosts = IPRange(ip_range[0], ip_range[1])
        except AddrFormatError:
            try:
                start_ip = IPAddress(ip_range[0])

                start_ip_words = list(start_ip.words)
                start_ip_words[-1] = ip_range[1]
                start_ip_words = [str(v) for v in start_ip_words]

                end_ip = IPAddress('.'.join(start_ip_words))

                t = IPRange(start_ip, end_ip)
            except AddrFormatError:
                t = target
    else:
        try:
            t = IPNetwork(target)
        except AddrFormatError:
            t = target

    if type(t) == IPNetwork or type(t) == IPRange:
        targets.extend(list(t))
    else:
        targets.append(t)

    return targets

####################################################################################
#
# Specific PowerShell helpers
#
####################################################################################

def enc_powershell(raw):
    """
    Encode a PowerShell command into a form usable by powershell.exe -enc ...
    """
    return base64.b64encode("".join([char + "\x00" for char in unicode(raw)]))


def powershell_launcher_arch(raw):
    """
    Build a one line PowerShell launcher with an -enc command.
    Architecture independent.
    """
    # encode the data into a form usable by -enc
    encCMD = enc_powershell(raw)

    # get the correct PowerShell path and set it temporarily to %pspath%
    triggerCMD = "if %PROCESSOR_ARCHITECTURE%==x86 (set pspath='') else (set pspath=%WinDir%\\syswow64\\windowspowershell\\v1.0\\)&"
    
    # invoke PowerShell with the appropriate options
    # triggerCMD += "call %pspath%powershell.exe -NoP -NonI -W Hidden -Exec Bypass -Enc " + encCMD
    triggerCMD += "call %pspath%powershell.exe -NoP -NonI -W Hidden -Enc " + encCMD

    return triggerCMD


def powershell_launcher(raw):
    """
    Build a one line PowerShell launcher with an -enc command.
    """
    # encode the data into a form usable by -enc
    encCMD = enc_powershell(raw)

    return "powershell.exe -NoP -NonI -W Hidden -Enc " + encCMD

def change_function_name(data, obfs_function_name):
    '''
    Changes the Powershell scripts function name
    '''

    return re.sub(re.compile('function Invoke-.*?\n{'), 'function Invoke-{}\n{'.format(obfs_function_name), data)

def strip_powershell_comments(data):
    """
    Strip block comments, line comments, empty lines, verbose statements,
    and debug statements from a PowerShell source file.
    """

    # strip block comments
    strippedCode = re.sub(re.compile('<#.*?#>', re.DOTALL), '', data)

    # strip blank lines, lines starting with #, and verbose/debug statements
    strippedCode = "\n".join([line for line in strippedCode.split('\n') if ((line.strip() != '') and (not line.strip().startswith("#")) and (not line.strip().lower().startswith("write-verbose ")) and (not line.strip().lower().startswith("write-debug ")) )])
    
    return strippedCode