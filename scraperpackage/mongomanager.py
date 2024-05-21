from os import getenv
from pymongo import MongoClient
from urllib.parse import quote_plus
from sshtunnel import SSHTunnelForwarder

class MongoManager(object):

    def __init__(self):
        self.use_ssh = getenv('USESSH') == 'True'

        if self.use_ssh:
            self.ssh_tunnel = SSHTunnelForwarder(
                getenv('SSHHOST'),
                ssh_username = getenv('SSHUSER'),
                ssh_password = getenv('SSHPASS'),
                remote_bind_address = (getenv('MONGOHOST'), int(getenv('MONGOPORT')))
            )
    
    @staticmethod
    def get_mongo_db(port):
        return MongoClient(
            getenv('MONGOHOST'),
            port,
            username = quote_plus(getenv('DBUSER')),
            password = quote_plus(getenv('DBPASS')),
        )[getenv('DBNAME')]

    def __enter__(self):
        if self.use_ssh:
            self.ssh_tunnel.start()
            return self.get_mongo_db(self.ssh_tunnel.local_bind_port)
        else:
            return self.get_mongo_db(int(getenv('MONGOPORT')))
    
    def __exit__(self, type, value, traceback):
        if self.use_ssh:
            self.ssh_tunnel.stop()
