import socket
from impacket.nmb import NetBIOSError
from impacket.smbconnection import SMBConnection, SessionError

class Module():

    def __init__(self, mainMenu):

        self.mainMenu = mainMenu

        self.info = {

            'Name': 'SMB Login Check Scanner',
            'Author': ['@byt3bl33d3r'],
            'OpsecSafe' : True,
            'Description': ('This module will test a SMB login on a range of machines and report successful logins.'),

        }

        self.options = {

            'RHOSTS' : {

                'Description'   : 'Remote hosts',
                'Required'      : True,
                'Value'         : ''
            },

            'RPORT' : {
                
                'Description'   : 'Remote SMB port',
                'Required'      : True,
                'Value'         : '445'
            },

            'SMBDomain' : {
                'Description'   : 'The Windows domain to use for authentication',
                'Required'      : False,
                'Value'         : ''

            },

            'SMBUser' : {
                'Description'  : 'The username to  authenticate as',
                'Required'     : False,
                'Value'        : ''

            },

            'SMBPass' : {
                'Description'  : 'The password for the specified username',
                'Required'     : False,
                'Value'        : ''

            },

            'HASH' : {
                'Description'  : 'The NTLM hash for the specified username',
                'Required'     : False,
                'Value'        : ''

            }
        }

    def run(self, target):

        smb_port   = int(self.options['RPORT']['Value'])
        smb_user   = self.options['SMBUser']['Value']
        smb_pass   = self.options['SMBPass']['Value']
        smb_domain = self.options['SMBDomain']['Value']
        ntlm_hash  = self.options['HASH']['Value']

        try:

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

            if not smb_domain:
                smb_domain = domain

            self.mainMenu.db.add_host(target, hostname, domain, os)

            try:
                '''
                    DC's seem to want us to logoff first
                    Windows workstations sometimes reset the connection, so we handle both cases here
                    (go home Windows, you're drunk)
                '''
                smb.logoff()
            except NetBIOSError:
                pass
            except socket.error:
                pass

            smb = SMBConnection(target, target, None, smb_port)

            try:
                if smb_pass:
                    smb.login(smb_user, smb_pass, smb_domain, '', '')
                    print "{}:{} {}\{}:{} Login Successful".format(target, smb_port, smb_domain, smb_user, smb_pass)
                    self.mainMenu.db.add_credential('cleartext', smb_domain, smb_user, smb_pass, target)

                elif ntlm_hash:
                    lmhash, nthash = ntlm_hash.split(':')
                    smb.login(smb_user, '', smb_domain, lmhash, nthash)
                    print "{}:{} {}\{}:{} Login Successful".format(target, smb_port, smb_domain, smb_user, ntlm_hash)
                    self.mainMenu.db.add_credential('hash', smb_domain, smb_user, ntlm_hash, target)

            except SessionError as e:
                print "{}:{} {}".format(target, smb_port, e)


        except NetBIOSError:
            return

        except socket.error:
            return