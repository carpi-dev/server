from argparse import ArgumentParser
from carpi_server.libs.Server import Server, Database
from carpi_server.libs.Builder import Builder

from sys import platform
import os


def get_os_specific(win, linux):
    if platform.startswith("win"):
        return win
    elif platform.startswith("linux"):
        return linux
    else:
        print("This was not tested on '{0}'.".format(platform))


def get_appdata_path():
    return os.getenv("APPDATA")


def get_work_dir():
    return get_os_specific("{0}\\carpi\\work\\".format(get_appdata_path()), "/tmp/carpi/work/")


def get_output_dir():
    return get_os_specific("{0}\\carpi\\output\\".format(get_appdata_path()), "/var/lib/carpi/modules/")


def get_database_file():
    return get_os_specific("{0}\\carpi\\database\\carpi.db".format(get_appdata_path()),
                           "/var/lib/carpi/database/carpi.db")


def main():
    ap = ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1", type=str)
    ap.add_argument("--port", default=8080, type=int)
    ap.add_argument("-sk", "--ssl-key", default=None, type=str)
    ap.add_argument("-sc", "--ssl-cert", default=None, type=str)
    ap.add_argument("-cu", "--create-user", default=False, type=bool)
    ap.add_argument("-du", "--delete-user", default=False, type=bool)
    ap.add_argument("-u", "--username", type=str)
    ap.add_argument("-db", "--database", default=get_database_file(), type=str)
    ap.add_argument("--enable-login", default=False, type=bool)
    ap.add_argument("--work-dir", default=get_work_dir(), type=str)
    ap.add_argument("--output-dir", default=get_output_dir(), type=str)
    a = ap.parse_args()

    db = Database(a.database)

    if a.create_user:
        if a.username is None:
            print("Can't create a user if you don't provide a username.")
            exit()
        if db.create_user(a.username):
            print("Created user '{0}'.".format(a.username))
        else:
            print("Could not create user '{0}'.".format(a.username))

    if a.delete_user:
        if a.username is None:
            print("Can't delete a user if you don't provider a username.")
            exit()
        if db.delete_user(a.username):
            print("Deleted user '{0}'.".format(a.username))
        else:
            print("Could not delete user '{0}'.".format(a.username))

    builder = Builder(db, a.work_dir, a.output_dir)
    srv = Server(db, builder)

    try:
        print("Starting builder.")
        builder.start()
        print("Starting server.")
        srv.start(a.host, a.port, a.ssl_cert, a.ssl_key)
    except KeyboardInterrupt:
        print("\nCaught CTRL+C, stopping all jobs.")
        print("Stopping server.")
        srv.stop()
        print("Stopping builder.")
        builder.stop()
    print("Done.")


if __name__ == '__main__':
    main()
