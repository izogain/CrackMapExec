import socket
from impacket.nmb import NetBIOSError
from impacket.smbconnection import SMBConnection, SessionError

class Module():

    def __init__(self, mainMenu):

        self.mainMenu = mainMenu

        self.info = {

            'Name': 'SMB Version Detection',
            'Author': ['@byt3bl33d3r'],
            'OpsecSafe' : True,
            'Description': ('Displays version information about each system'),
        }

        self.options = {

            'RHOSTS' : {
                'Description'   :   'Remote hosts',
                'Required'      :   True,
                'Value'         :   ''
            },

            'RPORT' : {
                'Description'   :  'Remote SMB port',
                'Required'      :   True,
                'Value'         :   '445'
            }
        }

    def run(self, target):
        try:

            smb_port = int(self.options['RPORT']['Value'])

            smb = SMBConnection(target, target, None, smb_port)
            try:
                smb.login('' , '')
            except SessionError as e:
                if "STATUS_ACCESS_DENIED" in e.message:
                    pass

            os = smb.getServerOS()
            hostname = smb.getServerName()
            domain = smb.getServerDomain()
            if not domain:
                domain = hostname

            print "{}:{} {} (name:{}) (domain:{})".format(target, smb_port, os, hostname, domain)
            self.mainMenu.db.add_host(target, hostname, domain, os)

            smb.logoff()

        except NetBIOSError:
            return

        except socket.error:
            return