from flask import Flask, request, abort, render_template, redirect, make_response, current_app
from flask.views import View
from functools import wraps
from flask.ext.login import login_user, current_user

import portality.models as models
from portality.core import app#, login_manager
from portality import settings
from portality.api import RegistryAPI

import json
from datetime import datetime

#from portality.view.account import blueprint as account

'''
User auth stuff, which we need to enable later

@login_manager.user_loader
def load_account_for_login_manager(userid):
    out = models.Account.pull(userid)
    return out

@app.context_processor
def set_current_context():
    return dict(current_user=current_user, app=app)

@app.before_request
def standard_authentication():
    """Check remote_user on a per-request basis."""
    remote_user = request.headers.get('REMOTE_USER', '')
    if remote_user:
        user = models.Account.pull(remote_user)
        if user:
            login_user(user, remember=False)
    # add a check for provision of api key
    elif 'api_key' in request.values:
        res = models.Account.query(q='api_key:"' + request.values['api_key'] + '"')['hits']['hits']
        if len(res) == 1:
            user = models.Account.pull(res[0]['_source']['id'])
            if user:
                login_user(user, remember=False)
'''

def jsonp(f):
    """Wraps JSONified output for JSONP"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            res = f(*args,**kwargs)
            toreturn = res
            if isinstance(res, tuple):
                res = res[0]
            if hasattr(res, "data"):
                res = res.data
            content = str(callback) + '(' + str(res) + ')'
            return current_app.response_class(content, mimetype='application/javascript')
        else:
            return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def root():
    return render_template("index.html")

#################################################################
## Endpoints for accessing the API
#################################################################

@app.route("/record/<record_id>/stat/<stat_id>", methods=["DELETE"])
def stat(record_id, stat_id):
    # delete the identified statistic
    # authenticated/authorised
    pass

@app.route("/record/<record_id>/stats", methods=["GET", "POST"])
def stats(record_id):
    if request.method == "GET":
        from_date = request.values.get("from") # <date to provide stats from>
        until_date = request.values.get("until") # <date to provide stats until>
        provider = request.values.get("provider") # <name of third party who generated the stats>
        stat_type = request.values.get("type") # <type of statistic to return>
        
        statistics = RegistryAPI.get_statistics(record_id, from_date=from_date, until_date=until_date, provider=provider, stat_type=stat_type)
        
        # return a json response
        resp = make_response(json.dumps(statistics))
        resp.mimetype = "application/json"
        return resp
        
    elif request.method == "POST":
        # add a new statistic
        # authenticated/authorised
        pass

@app.route("/record/<record_id>/admin", methods=["PUT"])
@jsonp
def admin(record_id):
    # replace an existing admin record
    # authenticated/authorised
    pass

@app.route("/record/<record_id>/history", methods=["GET"])
@jsonp
def history(record_id):
    # get the history of an object
    from_date = request.values.get("from") # <date to get the history stats from>
    until_date = request.values.get("until") # <date to provide history until>
    
    h = RegistryAPI.get_history(record_id, from_date=from_date, until_date=until_date)
    if h is None or len(h) == 0:
        abort(404)
    
    # return a json response
    resp = make_response(json.dumps(h))
    resp.mimetype = "application/json"
    return resp

@app.route("/record/<record_id>", methods=["GET", "POST", "PUT", "DELETE"])
@jsonp
def record(record_id):
    
    if request.method == "GET":
        # retrieve the record
        # unauthenticated
        register = RegistryAPI.get_registry_entry(record_id)
        if register is None:
            abort(404)
        # return a json response
        resp = make_response(register.json)
        resp.mimetype = "application/json"
        return resp
    
    elif request.method == "POST":
        # check that we are authorised
        apikey = request.values.get("api_key")
        acc = models.Account.pull_by_auth_token(apikey)
        if acc is None:
            abort(401)
        if not acc.registry_access:
            abort(401)
        
        # check that the record being updated exists
        reg = models.Register.pull(record_id)
        if reg is None:
            abort(404)
        
        # update the record
        try:
            newregister = json.loads(request.data)
        except:
            abort(400)
        
        RegistryAPI.update_register(acc, reg, newregister)
        
        # return a json response
        resp = make_response(json.dumps({"success" : "true"}))
        resp.mimetype = "application/json"
        return resp
    
    elif request.method == "PUT":
        # check that we are authorised
        apikey = request.values.get("api_key")
        acc = models.Account.pull_by_auth_token(apikey)
        if acc is None:
            abort(401)
        if not acc.registry_access:
            abort(401)
        
        # check that the record being updated exists
        reg = models.Register.pull(record_id)
        if reg is None:
            abort(404)
        
        # replace the record
        try:
            newregister = json.loads(request.data)
        except:
            abort(400)
        
        RegistryAPI.replace_register(acc, reg, newregister)
        
        # return a json response
        resp = make_response(json.dumps({"success" : "true"}))
        resp.mimetype = "application/json"
        return resp
        
    elif request.method == "DELETE":
        # check that we are authorised
        apikey = request.values.get("api_key")
        acc = models.Account.pull_by_auth_token(apikey)
        if acc is None:
            abort(401)
        if not acc.registry_access:
            abort(401)
        
        # check that the record being updated exists
        reg = models.Register.pull(record_id)
        if reg is None:
            abort(404)
        
        # delete it
        RegistryAPI.delete_register(acc, reg)
        
        # return a json response
        resp = make_response(json.dumps({"success" : "true"}))
        resp.mimetype = "application/json"
        return resp

@app.route("/record", methods=["POST"])
@jsonp
def create_record():
    # check that we are authorised
    apikey = request.values.get("api_key")
    acc = models.Account.pull_by_auth_token(apikey)
    if acc is None:
        abort(401)
    if not acc.registry_access:
        abort(401)
    
    # create the new record
    try:
        newregister = json.loads(request.data)
    except:
        abort(400)
    
    try:
        id = RegistryAPI.create_register(acc, newregister)
    except:
        abort(400)
    
    # return a json response
    resp = make_response(json.dumps({"success" : "true", "id" : id, "location" : "/record/" + id}))
    resp.headers["Location"] = "/record/" + id
    resp.mimetype = "application/json"
    resp.status_code = 201
    return resp

@app.route("/query", methods=["GET"])
@jsonp
def query():
    # extract all the potential query arguments
    es = request.values.get("es") # <elasticsearch query object>
    if es is None:
        es = request.values.get("source") # alternative location for the es query object
    q = request.values.get("q") # <free text search>
    fields = request.values.get("fields") # <list of top level fields required>
    from_number = request.values.get("from") # <start result number>
    size = request.values.get("size") # <page size>
    
    # the es argument is an encoded json string
    if es is not None:
        es = json.loads(es)
    
    print es
    
    # fields is a comma separated list of values
    # which may consist only of "admin" or "register"
    if fields is not None:
        fields = [f.strip() for f in fields.split(",") if f.strip() in ["admin", "register"]]
    
    es_result = RegistryAPI.search(es=es, q=q, fields=fields, from_number=from_number, size=size)
    
    # return a json response
    resp = make_response(json.dumps(es_result))
    resp.mimetype = "application/json"
    return resp

@app.route("/change", methods=["GET"])
@jsonp
def change():
    from_date = request.values.get("from") # <date to provide changes from>
    until_date =  request.values.get("until") # <date to provide changes until>
    from_number = request.values.get("from") # <start result number>
    size = request.values.get("size") # <page size>
    
    # need to check that the dates are correct
    if from_date is not None and not _validate_date(from_date):
        abort(400)
    if until_date is not None and not _validate_date(until_date):
        abort(400)
    
    es_result = RegistryAPI.change_list(from_date=from_date, until_date=until_date, from_number=from_number, size=size)
    
    # return a json response
    resp = make_response(json.dumps(es_result))
    resp.mimetype = "application/json"
    return resp

def _validate_date(date):
    try: 
        datetime.strptime("%Y-%m-%dT%H:%M:%SZ", date)
        return True
    except: pass
    
    try: 
        datetime.strptime("%Y-%m-%d", date)
        return True
    except: pass
    
    return False


##################################################################

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=app.config['DEBUG'], port=app.config['PORT'])

