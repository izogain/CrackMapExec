import os
import imp
import fnmatch

class Payloads:

    def __init__(self, mainMenu):
        self.mainMenu = mainMenu
        self.payloads = {}

    def load_payloads(self):
        """
        Load payloads from the payloads/* path
        """

        rootPath = 'payloads/'
        pattern = '*.py'

        for root, dirs, files in os.walk(rootPath):
            for filename in fnmatch.filter(files, pattern):
                filePath = os.path.join(root, filename)

                # don't load up the example
                if filename == "example_payload.py": continue
                
                # extract just the module name from the full path
                payloadName = filePath.split("payloads/")[-1][0:-3]

                # TODO: extract and CLI arguments and pass onto the modules

                # instantiate the module and save it to the internal cache
                self.payloads[payloadName] = imp.load_source(payloadName, filePath).Payload(self.mainMenu)

    def reload_payload(self, payloadToReload):
        """
        Reload a specific module
        """

        rootPath = 'payloads/'
        pattern = '*.py'
         
        for root, dirs, files in os.walk(rootPath):
            for filename in fnmatch.filter(files, pattern):
                filePath = os.path.join(root, filename)

                # don't load up the template
                if filename == "example_payload.py": continue
                
                # extract just the module name from the full path
                payloadName = filePath.split("payloads/")[-1][0:-3]

                # check to make sure we've found the specific module
                if payloadName.lower() == payloadToReload.lower():
                    # instantiate the module and save it to the internal cache
                    self.payloads[payloadName] = imp.load_source(payloadName, filePath).Module(self.mainMenu)

    def search_payloads(self, searchTerm):
        """
        Search currently loaded module names and descriptions.
        """

        #print ""

        for payloadName, payload in self.payloads.iteritems():
            if searchTerm.lower() == '' or searchTerm.lower() in payloadName.lower() or searchTerm.lower() in payload.info['Description'].lower():
                messages.display_module_search(payloadName, payload)

            # for comment in module.info['Comments']:
            #     if searchTerm.lower() in comment.lower():
            #         messages.display_module_search(moduleName, module)
