import os
import imp
import fnmatch

class Modules:

    def __init__(self, mainMenu):
        self.mainMenu = mainMenu
        self.modules = {}

    def load_modules(self):
        """
        Load modules from the modules/* path
        """

        rootPath = 'modules/'
        pattern = '*.py'

        for root, dirs, files in os.walk(rootPath):
            for filename in fnmatch.filter(files, pattern):
                filePath = os.path.join(root, filename)

                # don't load up the example
                if filename == "example_module.py": continue
                
                # extract just the module name from the full path
                moduleName = filePath.split("modules/")[-1][0:-3]

                # TODO: extract and CLI arguments and pass onto the modules

                # instantiate the module and save it to the internal cache
                self.modules[moduleName] = imp.load_source(moduleName, filePath).Module(self.mainMenu)

    def reload_module(self, moduleToReload):
        """
        Reload a specific module
        """

        rootPath = 'modules/'
        pattern = '*.py'
         
        for root, dirs, files in os.walk(rootPath):
            for filename in fnmatch.filter(files, pattern):
                filePath = os.path.join(root, filename)

                # don't load up the template
                if filename == "example_module.py": continue
                
                # extract just the module name from the full path
                moduleName = filePath.split("modules/")[-1][0:-3]

                # check to make sure we've found the specific module
                if moduleName.lower() == moduleToReload.lower():
                    # instantiate the module and save it to the internal cache
                    self.modules[moduleName] = imp.load_source(moduleName, filePath).Module(self.mainMenu)

    def search_modules(self, searchTerm):
        """
        Search currently loaded module names and descriptions.
        """

        #print ""

        for moduleName,module in self.modules.iteritems():
            if searchTerm.lower() == '' or searchTerm.lower() in moduleName.lower() or searchTerm.lower() in module.info['Description'].lower():
                messages.display_module_search(moduleName, module)

            # for comment in module.info['Comments']:
            #     if searchTerm.lower() in comment.lower():
            #         messages.display_module_search(moduleName, module)
