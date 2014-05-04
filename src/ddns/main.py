import flask
from flask import request

from ddns import models
from ddns.driver import Driver


app = flask.Flask("ddns")


def auth(func):
    def auth_wrapper(*args, **kwargs):
        return func(user=user, *args, **kwargs)
    return auth_wrapper


@app.route("/")
def index():
    return "DDNS"


@app.route("/host/update/<hostname>/")
def update_host(hostname):
    # users, keys, hosts = models.get_managers()
    ip_a = request.args['a']
    # ip_aaaa = request.args['aaaa']
    driver = Driver()
    driver.update_a(hostname, ip_a)
    return "ok"



# @app.route("/hosts/", methods=["GET", "POST"])
# def hosts():
#     user_id = request.args['user_id']
#     users, keys, hosts = models.get_managers()
#     user_keys = keys.filter(user=user_id)
#     user_hosts = hosts.filter(user=user_id)
#     print list(keys.filter())
#     import ipdb; ipdb.set_trace()


if __name__ == "__main__":
    app.run(debug=True)
