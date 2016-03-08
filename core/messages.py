"""

Common terminal messages.
"""

import os, sys, textwrap

def title(version):
    pass

def wrap_string(data, width=40, indent=32, indentAll=False, followingHeader=None):
    """
    Print a option description message in a nicely 
    wrapped and formatted paragraph.

    followingHeader -> text that also goes on the first line
    """

    data = str(data)

    if len(data) > width:
        lines = textwrap.wrap(textwrap.dedent(data).strip(), width=width)
        
        if indentAll:
            returnString = ' '*indent+lines[0]
            if followingHeader: 
                returnString += " " + followingHeader
        else:
            returnString = lines[0]
            if followingHeader: 
                returnString += " " + followingHeader
        i = 1
        while i < len(lines):
            returnString += "\n"+' '*indent+(lines[i]).strip()
            i += 1
        return returnString
    else:
        return data.strip()

def wrap_columns(col1, col2, width1=24, width2=40, indent=31):
    """
    Takes two strings of text and turns them into nicely formatted column output.

    Used by display_module()
    """
    
    lines1 = textwrap.wrap(textwrap.dedent(col1).strip(), width=width1)
    lines2 = textwrap.wrap(textwrap.dedent(col2).strip(), width=width2)

    result = ''

    limit = max(len(lines1), len(lines2))

    for x in xrange(limit):

        if x < len(lines1):
            if x != 0:
                result +=  ' '*indent
            result += '{line: <0{width}s}'.format(width=width1, line=lines1[x])
        else:
            if x == 0:
                result += ' '*width1
            else:
                result += ' '*(indent + width1)

        if x < len(lines2):
            result +=  '  ' + '{line: <0{width}s}'.format(width=width2, line=lines2[x])

        if x != limit-1:
            result += "\n"

    return result

def display_options(options, color=True):
    """
    Take a dictionary and display it nicely.
    """
    for key in options:
        if color:
            print "\t%s\t%s" % ('{0: <16}'.format(key), wrap_string(options[key]))
        else:
            print "\t%s\t%s" % ('{0: <16}'.format(key), wrap_string(options[key]))



    print ""

def display_module_info(moduleName, module):
    """
    Displays a module's information structure.
    """
    
    print '\n{0: >17}'.format("Name: ") + str(module.info['Name'])
    print '{0: >17}'.format("Module: ") + str(moduleName)
    #print '{0: >17}'.format("NeedsAdmin: ") + ("True" if module.info['NeedsAdmin'] else "False")
    print '{0: >17}'.format("OpsecSafe: ") + ("True" if module.info['OpsecSafe'] else "False")
    #print '{0: >17}'.format("MinPSVersion: ") + str(module.info['MinPSVersion'])
    #print '{0: >17}'.format("Background: ") + ("True" if module.info['Background'] else "False")
    #print '{0: >17}'.format("OutputExtension: ") + (str(module.info['OutputExtension']) if module.info['OutputExtension'] else "None")

    print "\nAuthors:"
    for author in module.info['Author']:
        print "  " +author

    print "\nDescription:"
    desc = wrap_string(module.info['Description'], width=60, indent=2, indentAll=True)
    if len(desc.splitlines()) == 1:
        print "  " + str(desc)
    else:
        print desc

    # print out any options, if present
    if module.options:

        # get the size for the first column
        maxNameLen = len(max(module.options.keys(), key=len))

        print "\nModule Options:\n"
        print "  %sRequired    Value                     Description" %('{:<{}s}'.format("Name", maxNameLen+1))
        print "  %s--------    -------                   -----------" %('{:<{}s}'.format("----", maxNameLen+1))

        for option,values in module.options.iteritems():
            print "  %s%s%s" % ('{:<{}s}'.format(str(option), maxNameLen+1), '{0: <12}'.format(("True" if values['Required'] else "False")), wrap_columns(str(values['Value']), str(values['Description']), indent=(31 + (maxNameLen-16))))

    print ""

def display_module_options(moduleName, module):
    """
    Displays a module's options.
    """
    # get the size for the first column
    maxNameLen = len(max(module.options.keys(), key=len))

    print "\nModule Options:\n"
    print "  %sRequired    Value                     Description" %('{:<{}s}'.format("Name", maxNameLen+1))
    print "  %s--------    -------                   -----------" %('{:<{}s}'.format("----", maxNameLen+1))

    for option,values in module.options.iteritems():
        print "  %s%s%s" % ('{:<{}s}'.format(str(option), maxNameLen+1), '{0: <12}'.format(("True" if values['Required'] else "False")), wrap_columns(str(values['Value']), str(values['Description']), indent=(31 + (maxNameLen-16))))

    print ""

def display_payload_options(payload):
    """
    Displays a module's options.
    """
    # get the size for the first column
    maxNameLen = len(max(payload.options.keys(), key=len))

    print "\nPayload Options:\n"
    print "  %sRequired    Value                     Description" %('{:<{}s}'.format("Name", maxNameLen+1))
    print "  %s--------    -------                   -----------" %('{:<{}s}'.format("----", maxNameLen+1))

    for option,values in payload.options.iteritems():
        print "  %s%s%s" % ('{:<{}s}'.format(str(option), maxNameLen+1), '{0: <12}'.format(("True" if values['Required'] else "False")), wrap_columns(str(values['Value']), str(values['Description']), indent=(31 + (maxNameLen-16))))

    print ""

def display_global_vars(globalvars):

    maxNameLen = len(max(globalvars.keys(), key=len))

    print "\nGlobals:\n"
    print "  %sRequired    Value                     Description" %('{:<{}s}'.format("Name", maxNameLen+1))
    print "  %s--------    -------                   -----------" %('{:<{}s}'.format("----", maxNameLen+1))

    for option,values in globalvars.iteritems():
        print "  %s%s%s" % ('{:<{}s}'.format(str(option), maxNameLen+1), '{0: <12}'.format(("True" if values['Required'] else "False")), wrap_columns(str(values['Value']), str(values['Description']), indent=(31 + (maxNameLen-16))))

    print ""

def display_module_search(moduleName, module):
    """
    Displays the name/description of a module for search results.
    """

    print " " + moduleName + "\n"
    # width=40, indent=32, indentAll=False,
    
    lines = textwrap.wrap(textwrap.dedent(module.info['Description']).strip(), width=70)
    for line in lines:
        print "\t" + line

    print "\n"


def display_hosts(hosts):

    print "\nHosts:\n"
    print "  HostID  IP         Hostname                 Domain           OS"
    print "  ------  --         --------                 ------           --"

    for host in hosts:
        # (id, ip, hostname, domain, os)
        hostID = host[0]
        ip = host[1]
        hostname = host[2]
        domain = host[3]
        os = host[4]

        print "  %s%s%s%s%s" % ('{0: <8}'.format(hostID), '{0: <11}'.format(ip), '{0: <25}'.format(hostname), '{0: <17}'.format(domain), '{0: <17}'.format(os))

    print ""


def display_credentials(creds):

    print "\nCredentials:\n"
    print "  CredID  CredType   Domain                   UserName         Host             Password"
    print "  ------  --------   ------                   --------         ----             --------"

    for cred in creds:
        # (id, credtype, domain, username, password, host, notes, sid)
        credID = cred[0]
        credType = cred[1]
        domain = cred[2]
        username = cred[3]
        password = cred[4]
        host = cred[5]

        print "  %s%s%s%s%s%s" % ('{0: <8}'.format(credID), '{0: <11}'.format(credType), '{0: <25}'.format(domain), '{0: <17}'.format(username), '{0: <17}'.format(host), password)

    print ""
