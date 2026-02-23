import MySQLdb
import sshtunnel

from classes import DatabaseSettings

sshtunnel.SSH_TIMEOUT = 10.0
sshtunnel.TUNNEL_TIMEOUT = 10.0

# TODO : https://help.pythonanywhere.com/pages/AccessingMySQLFromOutsidePythonAnywhere/
def db_connect(settings: DatabaseSettings):
    with sshtunnel.SSHTunnelForwarder(
            settings.ssh_hostname,
            ssh_username=settings.pa_username,
            ssh_password=settings.pa_password,
            remote_bind_address=(settings.pa_hostname, 3306)
    ) as tunnel:
        connection = MySQLdb.connect(
            user=settings.db_username,
            passwd=settings.db_password,
            host=settings.db_host,
            port=tunnel.local_bind_port,
            db=settings.db_name,
        )
        # Do stuff
        connection.close()
