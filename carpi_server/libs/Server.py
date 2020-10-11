from flask import Flask, make_response, render_template, redirect, request, send_from_directory
from gevent.pywsgi import WSGIServer

from .Database import Database
from .Builder import Builder


class Server(object):
    srv = None

    def __init__(self, database: Database, builder: Builder, login=False):
        self.login = login
        self.app = Flask(__name__)
        self.db = database
        self.builder = builder

        self.app.static_folder = "static"
        self.app.template_folder = "templates"

        @self.app.route("/")
        def root():
            return make_response(redirect("/dashboard"))

        @self.app.route("/dashboard")
        def dashboard():
            o = self.db.get_oldest_module()
            r = {}
            if o:
                r["notEnoughData"] = False
                r["moduleCreationTimelineTimespan"] = "{0} days".format(
                    self.db.get_timespan_date_days(self.db.parse_date(o)))
                r["moduleCreation"] = self.db.get_created_timeline_days()
            else:
                r["notEnoughData"] = True
            return self.redirect_or_not("dashboard.html", r)

        @self.app.route("/modules", methods=["POST", "GET"])
        def modules():
            return self.redirect_or_not("modules.html", {
                "modules": self.db.get_modules()
            })

        @self.app.route("/builder", methods=["POST", "GET"])
        def builder():
            return self.redirect_or_not("builder.html", {

            })

        @self.app.route("/login", methods=["POST", "GET"])
        def login():
            if not self.login:
                return make_response(redirect("/dashboard"))
            if request.method == "POST":
                data = request.form
                username = data["username"]
                password = data["password"]
                if self.db.check_username_password(username, password):
                    return make_response(render_template("login.html"))
                return make_response(render_template("login.html"))
            else:
                return make_response(render_template("login.html"))

        @self.app.route("/api/module/list")
        def api_module_list():
            return make_response(self.db.get_modules())

        @self.app.route("/api/module/<path:path>")
        def api_module(path):
            r = self.db.get_module(path)
            return make_response(r if r else {})

        @self.app.route("/api/module/<path:path>/binary")
        def api_module_binary(path):
            self.db.increment_module_download_count(path)
            return make_response(send_from_directory(self.builder.output_dir, path))

    def redirect_or_not(self, template, args):
        if not self.login:
            return make_response(render_template(template, **args))
        elif self.check_cookie():
            return make_response(render_template(template, **args))
        else:
            return redirect("/login")

    def check_cookie(self) -> bool:
        c = request.cookies.get("cookie")
        u = request.cookies.get("username")
        if c is None or u is None:
            return False
        return self.db.check_username_cookie(u, c)

    def start(self, host, port, cert=None, key=None):
        if cert and key:
            self.srv = WSGIServer((host, port), self.app, keyfile=key, certfile=cert)
        else:
            self.srv = WSGIServer((host, port), self.app)
        self.srv.serve_forever()

    def stop(self):
        self.srv.stop()
