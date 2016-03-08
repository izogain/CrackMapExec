#This must be one of the first imports or else we get threading error on completion
from gevent import monkey
monkey.patch_all()

import cmd
import sqlite3
import core.messages as messages
import core.helpers as helpers
from core.modules import Modules
from core.payloads import Payloads
from core.database import Database
from gevent.pool import Pool

class MainMenu(cmd.Cmd):

    def __init__(self):

        cmd.Cmd.__init__(self)
        self.prompt = 'cme > '

        self.globalOptions = {
                                'THREADS': {
                                    'Value': 100, 
                                    'Required': True, 
                                    'Description': 'Number of concurrent threads'
                               },

                              'THREAD_TIMEOUT': {
                                    'Value': 20, 
                                    'Required': True, 
                                    'Description': 'Timeout for each thread'
                               }
                            }

        try:
            # set the database connectiont to autocommit w/ isolation level
            self.conn = sqlite3.connect('data/cme.db', check_same_thread=False)
            self.conn.text_factory = str
            self.conn.isolation_level = None
        except Exception as e:
            print "Could not connect to database: {}".format(e)
            sys.exit()

        self.db = Database(self.conn)

        self.modules = Modules(self)
        self.modules.load_modules()

        self.payloads = Payloads(self)
        self.payloads.load_payloads()

    def do_module(self, line):
        if line not in self.modules.modules:
            print "invalid module"
        else:
            try:
                l = ModuleMenu(self, line)
                l.cmdloop()
            except Exception as e:
                raise e

    def do_globals(self, line):
        "Display global variables."
        messages.display_global_vars(self.globalOptions)

    def do_reload(self, line):
        "Reload one (or all) Empire modules."
        
        if line.strip().lower() == "all":
            # reload all modules
            print "\n" + "Reloading all modules."+ "\n"
            self.modules.load_modules()
        else:
            if line.strip() not in self.modules.modules:
                print "Error: invalid module"
            else:
                print "\n" + "Reloading module: " + line + "\n"
                self.modules.reload_module(line)

    def do_setg(self, line):

        "Set a global variable."

        parts = line.split()

        option = parts[0]
        value = " ".join(parts[1:])

        if value == '""' or value == "''": value = ""

        if option not in self.globalOptions:
            self.globalOptions[option] = {}
            self.globalOptions[option]['Description'] = ''
            self.globalOptions[option]['Required'] = False
        
        self.globalOptions[option]['Value'] = value

        for name,module in self.modules.modules.iteritems():
            if option in module.options.keys():
                module.options[option]['Value'] = value

    def do_hosts(self, line):
        hosts = self.db.get_hosts()
        messages.display_hosts(hosts)

    def do_creds(self, line):
        creds = self.db.get_credentials()
        messages.display_credentials(creds)

    def complete_module(self, text, line, begidx, endidx):

        modules = self.modules.modules.keys()

        mline = line.partition(' ')[2]
        offs = len(mline) - len(text)
        return [s[offs:] for s in modules if s.startswith(mline)]

    def complete_reload(self, text, line, begidx, endidx):

        modules = self.modules.modules.keys()

        mline = line.partition(' ')[2]
        offs = len(mline) - len(text)
        return [s[offs:] for s in modules if s.startswith(mline)]


    def complete_setg(self, text, line, begidx, endidx):
        "Tab-complete global variables to set"

        options = self.globalOptions.keys()

        # otherwise we're tab-completing an option name
        mline = line.partition(' ')[2]
        offs = len(mline) - len(text)
        return [s[offs:] for s in options if s.startswith(mline)]

class ModuleMenu(cmd.Cmd):

    def __init__(self, mainMenu, moduleName):

        cmd.Cmd.__init__(self)
        self.mainMenu = mainMenu
        self.moduleName = moduleName
        self.module = mainMenu.modules.modules[moduleName]
        self.prompt = 'cme ({}) > '.format(moduleName.split('/')[-1])

    def do_options(self, line):
        "Display module options"
        messages.display_module_options(self.moduleName, self.module)
        if hasattr(self.module, 'payload') and getattr(self.module, 'payload') is not None:
            messages.display_payload_options(self.module.payload)

    def do_info(self, line):
        "Display module info"
        messages.display_module_info(self.moduleName, self.module)
        if hasattr(self.module, 'payload') and getattr(self.module, 'payload') is not None:
            messages.display_payload_info(self.module.payload)

    def do_hosts(self, line):
        self.mainMenu.do_hosts(line)

    def do_creds(self, line):
        self.mainMenu.do_creds(line)

    def do_setg(self, line):
        self.mainMenu.do_setg(line)

    def do_globals(self, line):
        self.mainMenu.do_globals(line)

    def do_payload(self, line):
        if not hasattr(self.module, 'payload'):
            print 'This module does not support payloads'

        elif hasattr(self.module, 'payload'):
            if line not in self.mainMenu.payloads.payloads:
                print "Invalid payload"
            else:
                self.module.payload = self.mainMenu.payloads.payloads[line]

    def do_set(self, line):
        "Set a module option."

        parts = line.split()

        has_payload = False
        if hasattr(self.module, 'payload') and getattr(self.module, 'payload') is not None:
            has_payload = True

        try:
            option = parts[0]

            if option in self.module.options:
                # otherwise "set OPTION VALUE"
                option = parts[0]
                value = " ".join(parts[1:])
                
                if value == '""' or value == "''": value = ""

                self.module.options[option]['Value'] = value

            elif has_payload is True and option in self.module.payload.options:
                # otherwise "set OPTION VALUE"
                option = parts[0]
                value = " ".join(parts[1:])
                
                if value == '""' or value == "''": value = ""

                self.module.payload.options[option]['Value'] = value

            else:
                print "Invalid option name"

        except:
            print "Error in setting option, likely invalid option name."

    def do_unset(self, line):
        "Unset a module option."

        option = line.split()[0]

        if line.lower() == "all":
            for option in self.module.options:
                self.module.options[option]['Value'] = ''
        if option not in self.module.options:
            print "Invalid option specified."
        else:
            self.module.options[option]['Value'] = ''

    def do_run(self, line):
        targets = helpers.get_targets(self.module.options['RHOSTS']['Value'])
        threads = int(self.mainMenu.globalOptions['THREADS']['Value'])
        thread_timeout = int(self.mainMenu.globalOptions['THREAD_TIMEOUT']['Value'])

        if hasattr(self.module, 'payload'):
            self.module.payload.handler()

        try:
            pool = Pool(threads)
            jobs = [pool.spawn(self.module.run, str(target)) for target in targets]
            for job in jobs: 
                job.join(timeout=thread_timeout)
        except KeyboardInterrupt:
            print 'Caught CTRL-C'
            if hasattr(self.module, 'payload'):
                if hasattr(self.module.payload, 'server') and getattr(self.module.payload, 'server') is not None:
                    print 'Shutting down server'
                    self.module.payload.server.shutdown()
                    self.module.payload.server.socket.close()
                    self.module.payload.server.server_close()

    def do_back(self, line):
        "Return to the main menu."
        return True

    def complete_payload(self, text, line, begidx, endidx):

        payloads = self.mainMenu.payloads.payloads.keys()

        mline = line.partition(' ')[2]
        offs = len(mline) - len(text)
        return [s[offs:] for s in payloads if s.startswith(mline)]

    def complete_set(self, text, line, begidx, endidx):
        "Tab-complete a module option to set."

        options = self.module.options.keys()
        
        if hasattr(self.module, 'payload') and getattr(self.module, 'payload') is not None:
            options.extend(self.module.payload.options)

        # otherwise we're tab-completing an option name
        mline = line.partition(' ')[2]
        offs = len(mline) - len(text)
        return [s[offs:] for s in options if s.startswith(mline)]

    def complete_unset(self, text, line, begidx, endidx):
        "Tab-complete a module option to unset."

        options = self.module.options.keys() + ["all"]

        mline = line.partition(' ')[2]
        offs = len(mline) - len(text)
        return [s[offs:] for s in options if s.startswith(mline)]

    def complete_setg(self, text, line, begidx, endidx):
        "Tab-complete global variables to set"

        options = self.mainMenu.globalOptions.keys()

        # otherwise we're tab-completing an option name
        mline = line.partition(' ')[2]
        offs = len(mline) - len(text)
        return [s[offs:] for s in options if s.startswith(mline)]

if __name__ == '__main__':
    menu = MainMenu()
    menu.cmdloop()