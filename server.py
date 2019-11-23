
from hashlib import md5
import json, time
from flask import Flask, request, Response
from spider import Spider, register

app = Flask(__name__)

_mapping = {}
spiders = {}

@app.route('/login', methods=['POST'])
def login():
    global spiders, _mapping
    spider = Spider()
    register(spider)
    uname = request.form.get('uname', '')
    upass = request.form.get('upass', '')
    resp = spider.login_bv(uname, upass)
    if resp['code'] != 0:
        return Response('forbidden', 403)
    ts = int(time.time() * 1000)
    m = md5()
    token = uname + '&' + upass + '&' + str(ts)
    for _ in range(ts % 17):
        m.update(token.encode())
        token = m.hexdigest()
    if uname in _mapping:
        spiders.pop(_mapping[uname])
    _mapping[uname] = token
    spiders[token] = spider
    resp['token'] = token
    return json.dumps(resp)

@app.route('/get_projects', methods=['GET'])
def get_projects():
    global spiders, _mapping
    token = request.args.get('token', '')
    spider = spiders.get(token, None)
    if spider is None:
        return Response(response="forbidden", status=403)
    try:
        resp = spider.api['get_projects']()
    except:
        return Response(response="bad request", status=400)
    return json.dumps(resp)

@app.route('/generate_code', methods=['POST'])
def generate_code():
    global spiders, _mapping
    token = request.args.get('token', '')
    spider = spiders.get(token, None)
    if spider is None:
        return Response(response="forbidden", status=403)
    opp_id = request.form.get('opp_id', '')
    job_id= request.form.get('job_id', '')
    count= request.form.get('count', '')
    time= request.form.get('time', '')
    memo= request.form.get('memo', '')
    try:
        resp = spider.api['generate_code'](opp_id, job_id, count, time, memo)
    except:
        return Response(response="bad request", status=400)
    return json.dumps(resp)

@app.route('/get_code_list', methods=['GET'])
def get_code_list():
    global spiders, _mapping
    token = request.args.get('token', '')
    spider = spiders.get(token, None)
    if spider is None:
        return Response(response="forbidden", status=403)
    opp_id = request.args.get('opp_id', '')
    job_id= request.args.get('job_id', '')
    try:
        resp = spider.api['get_code_list'](opp_id, job_id)
    except:
        return Response(response="bad request", status=400)
    return json.dumps(resp)

@app.route('/use_code', methods=['POST'])
def user_code():
    global spiders, _mapping
    token = request.args.get('token', '')
    spider = spiders.get(token, None)
    if spider is None:
        return Response(response="forbidden", status=403)
    code = request.form.get('code', '')
    try:
        resp = spider.api['use_code'](code)
    except:
        return Response(response="bad request", status=400)
    return json.dumps(resp)

@app.route('/my_projects', methods=['GET'])
def my_projects():
    global spiders, _mapping
    token = request.args.get('token', '')
    spider = spiders.get(token, None)
    if spider is None:
        return Response(response="forbidden", status=403)
    try:
        resp = spider.api['my_projects']()
    except:
        return Response(response="bad request", status=400)
    return json.dumps(resp)

if __name__ == '__main__':
    app.run('0.0.0.0')
