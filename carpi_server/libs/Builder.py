from runnable import Runnable
from os import path
from os import listdir, makedirs, system
from time import sleep

from .Database import Database


class BuildState:
    IDLE = "idle"
    FETCHING = "fetching"
    CLONING = "cloning;"
    PULLING = "pulling;"
    BUILDING = "building;"


class Builder(Runnable):
    def __init__(self, db: Database, work_dir="/tmp/carpi/work/", output_dir="/var/lib/carpi/modules"):
        Runnable.__init__(self)
        self.work_dir = path.abspath(work_dir)
        self.output_dir = path.abspath(output_dir)
        self.create_dirs([self.work_dir, self.output_dir])
        self.db = db
        self.state = BuildState.IDLE

    @staticmethod
    def create_dirs(directories):
        for directory in directories:
            if not path.isdir(directory):
                print("Creating directory {0}.".format(directory))
                makedirs(directory, exist_ok=True)

    @staticmethod
    def get_build_path(directory):
        build_path = path.abspath(path.join(directory, "build"))
        if not path.isdir(build_path):
            makedirs(build_path)
        return build_path

    @classmethod
    def cmake_build(cls, directory, parameters=[]):
        build_path = cls.get_build_path(directory)
        system("cd {0}; cmake .. {1}; make -j($nproc)".format(build_path, ' '.join(parameters)))

    @staticmethod
    def configure_build(directory):
        system("cd {0}; ./configure; make -j($nproc)".format(directory))

    def build(self, directory):
        self.state = BuildState.BUILDING + directory
        files = listdir(directory)
        if "CMakeList.txt" in files:
            self.cmake_build(directory)
        elif "configure" in files:
            self.configure_build(directory)
        else:
            print("Could not figure out build method for project '{0}'.".format(directory))

    def clone(self, url, name):
        self.state = BuildState.CLONING + "name;url"
        system("cd {0}; git clone {1} {2}".format(self.work_dir, url, name))

    def pull(self, name):
        self.state = BuildState.PULLING + name
        system("cd {0}; git pull".format(path.join(self.work_dir, name)))

    def fetch(self):
        self.state = BuildState.FETCHING
        for m in self.db.get_modules():
            if not path.isdir(path.join(self.work_dir, m["name"])):
                self.clone(m["url"], m["name"])
            else:
                self.pull(m["name"])

    def work(self):
        self.fetch()
        for directory in listdir(self.work_dir):
            self.build(path.abspath(directory))
        sleep(30)
