class Database:

    def __init__(self, conn):
        self.conn = conn

    def is_credential_valid(self, credentialID):
        """
        Check if this credential ID is valid.
        """
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM credentials WHERE id=? limit 1', [credentialID])
        results = cur.fetchall()
        cur.close()
        return len(results) > 0

    def is_credential_duplicate(self, credtype, domain, username, password, host):
        """
        Check if this credential has already been added to the database
        """
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM credentials WHERE LOWER(credtype) LIKE LOWER(?) and WHERE LOWER(domain) LIKE LOWER(?) and WHERE LOWER(username) LIKE LOWER(?) and WHERE LOWER(password) LIKE LOWER(?) and WHERE LOWER(host) LIKE LOWER(?)', [credtype, domain, username, password, host])
        results = cur.fetchall()
        cur.close()
        return len(results) > 0

    def is_host_duplicate(self, ip):

        """
        Check if this host has already been added to the database
        """
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM hosts WHERE LOWER(ip) LIKE LOWER(?)', [ip])
        results = cur.fetchall()
        cur.close()
        return len(results) > 0

    def add_host(self, ip, hostname, domain, os):
        """
        Add a host with the specified information to the database.
        """
        if not self.is_host_duplicate(ip):
            cur = self.conn.cursor()
            cur.execute("INSERT INTO hosts (ip, hostname, domain, os) VALUES (?,?,?,?)", [ip, hostname, domain, os] )
            cur.close()

    def add_credential(self, credtype, domain, username, password, host, sid="", notes=""):
        """
        Add a credential with the specified information to the database.
        """
        if not is_credential_duplicate(credtype, domain, username, password, host):
            cur = self.conn.cursor()
            cur.execute("INSERT INTO credentials (credtype, domain, username, password, host, sid, notes) VALUES (?,?,?,?,?,?,?)", [credtype, domain, username, password, host, sid, notes] )
            cur.close()

    def get_hosts(self, filterTerm=None, credtype=None, note=None):
        """
        Return credentials from the database.

        'credtype' can be specified to return creds of a specific type.
        Values are: hash, plaintext, and token.
        """

        cur = self.conn.cursor()
        '''
        # if we're returning a single credential by ID
        if self.is_credential_valid(filterTerm):
            cur.execute("SELECT * FROM credentials WHERE id=? limit 1", [filterTerm])

        # if we're filtering by host/username
        elif filterTerm and filterTerm != "":
            cur.execute("SELECT * FROM credentials WHERE LOWER(host) LIKE LOWER(?) or LOWER(username) like LOWER(?)", [filterTerm, filterTerm])

        # if we're filtering by credential type (hash, plaintext, token)
        elif(credtype and credtype != ""):
            cur.execute("SELECT * FROM credentials WHERE LOWER(credtype) LIKE LOWER(?)", [credtype])

        # if we're filtering by content in the note field
        elif(note and note != ""):
            cur.execute("SELECT * FROM credentials WHERE LOWER(note) LIKE LOWER(%?%)", [note])

        # otherwise return all credentials            
        else:
        '''
        cur.execute("SELECT * FROM hosts")

        results = cur.fetchall()
        cur.close()

        return results

    def get_credentials(self, filterTerm=None, credtype=None, note=None):
        """
        Return credentials from the database.

        'credtype' can be specified to return creds of a specific type.
        Values are: hash, plaintext, and token.
        """

        cur = self.conn.cursor()

        # if we're returning a single credential by ID
        if self.is_credential_valid(filterTerm):
            cur.execute("SELECT * FROM credentials WHERE id=? limit 1", [filterTerm])

        # if we're filtering by host/username
        elif filterTerm and filterTerm != "":
            cur.execute("SELECT * FROM credentials WHERE LOWER(host) LIKE LOWER(?) or LOWER(username) like LOWER(?)", [filterTerm, filterTerm])

        # if we're filtering by credential type (hash, plaintext, token)
        elif(credtype and credtype != ""):
            cur.execute("SELECT * FROM credentials WHERE LOWER(credtype) LIKE LOWER(?)", [credtype])

        # if we're filtering by content in the note field
        elif(note and note != ""):
            cur.execute("SELECT * FROM credentials WHERE LOWER(note) LIKE LOWER(%?%)", [note])

        # otherwise return all credentials            
        else:
            cur.execute("SELECT * FROM credentials")

        results = cur.fetchall()
        cur.close()

        return results