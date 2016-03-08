class Module():

    def __init__(self, mainMenu):

        self.mainMenu = mainMenu

        # metadata info about the module, not modified during runtime
        self.info = {
            # name for the module that will appear in module menus
            'Name': 'Example Module',

            # list of one or more authors for the module
            'Author': ['@yourname'],

            'OpsecSafe' : False,

            # more verbose multi-line description of the module
            'Description': ('description line 1'
                            'description line 2'),

            # list of any references/other comments
            'Comments': [
                'comment',
                'http://link/'
            ]
        }

        # any options needed by the module, settable during runtime
        self.options = {
            # format:
            #   value_name : {description, required, default_value}
            'RHOSTS' : {
                # The 'RHOSTS' option is the only one that MUST be in a module
                'Description'   :   'Remote hosts',
                'Required'      :   True,
                'Value'         :   ''
            }
        }

    def run(self, target):
        '''Put your code here. Will be executed concurrently with gevent'''
        pass