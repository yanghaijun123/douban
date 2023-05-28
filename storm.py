#!/usr/bin/env python
# coding: utf-8
import json
import base64
import tornado.web
import tornado.ioloop


users = {
        1: {
            'id': 1,
            'name': '小明',
            'age': 18,
            'money': 1000
            }
        }


class GetUserHandler(tornado.web.RequestHandler):
    json_header = True
    def get(self):
        uid = self.get_argument('userid', 1)
        user = users.get(int(uid), None)
        if not user:
            return self.write({'code':500, 'msg': '没有这个用户'})
        username = user.get('name', '')
        userage = user.get('age', 18)
        if self.json_header:
            self.set_header('Content-Type', 'application/json')
        return self.write(json.dumps({'code': 200, 'id':uid,
                           'name': username,
                           'age': userage}))

    def post(self):
        return self.get()

class GetUser2Handler(GetUserHandler):
    json_header = True
    def get(self):
        ctype = self.request.headers.get('Content-Type', '')
        if ctype != 'application/json':
            return self.write({'code':500, 'msg': '请设置Content-Type为application/json'})
        uid = self.get_argument('userid', 1)
        user = users.get(int(uid), None)
        if not user:
            return self.write({'code':500, 'msg': '没有这个用户'})
        username = user.get('name', '')
        userage = user.get('age', 18)
        if self.json_header:
            self.set_header('Content-Type', 'application/json')
        return self.write(json.dumps({'code': 200, 'id':uid,
                           'name': username,
                           'age': userage}))

    def post(self):
        return self.get()

class GetMoneyHandler(tornado.web.RequestHandler):
    def post(self):
        try:
            args = json.loads(self.request.body.decode('utf-8'))
        except ValueError:
            return self.write({'code':500, 'msg': '参数错误'})
        uid = args.get('userid', 1)
        user = users.get(uid, None)
        if not user:
            return self.write({'code':500, 'msg': '没有这个用户'})
        user_money = user.get('money', 0)
        return self.write({'code': 200, 'userid':uid, 'money': user_money})

class SetMoneyHandler(tornado.web.RequestHandler):
    def post(self):
        auth = self.request.headers.get('Authorization')
        if not auth:
            return self.write({'code':500, 'msg': '需要认证'})
        if not auth.startswith('Basic'):
            return self.write({'code':500, 'msg': '只支持Basic认证'})
        try:
            decoded_auth = base64.urlsafe_b64decode(auth.split()[-1]).decode('utf-8')
        except Exception as e:
            return self.write({'code':500, 'msg': '认证失败'})
        if len(decoded_auth.split(':')) != 2:
            return self.write({'code':500, 'msg': '认证失败'})
        username, passwd = decoded_auth.split(':')
        if username != 'admin' or passwd != '123456':
            return self.write({'code':500, 'msg': '认证失败'})
        uid = self.get_argument('userid', 1)
        money = self.get_argument('money', None)
        if money is None:
            return self.write({'code':500, 'msg': '没有传递金额'})
        user = users.get(int(uid), None)
        if not user:
            return self.write({'code':500, 'msg': '没有这个用户'})
        user['money'] = int(money)
        return self.write({'code': 200, 'success': '成功'})

class SetMoney2Handler(tornado.web.RequestHandler):
    def post(self):
        token = self.get_cookie('token')
        if not token:
            return self.write({'code':500, 'msg': 'cookie认证失败'})
        if token != 'token12345':
            return self.write({'code':500, 'msg': 'cookie非法'})
        uid = self.get_argument('userid', 1)
        money = self.get_argument('money', None)
        if money is None:
            return self.write({'code':500, 'msg': '没有传递金额'})
        user = users.get(int(uid), None)
        if not user:
            return self.write({'code':500, 'msg': '没有这个用户'})
        user['money'] = int(money)
        return self.write({'code': 200, 'success': '成功'})


class UploadFileHandler(tornado.web.RequestHandler):
    def post(self):
        upf = self.request.files.get('file')
        if not upf:
            return self.write({'code': 500, 'success': '未上传文件'})
        upf = upf[0]
        fname = upf['filename']
        fcont = upf['body']
        with open(fname, 'w') as wf:
            wf.write(fcont.decode('utf-8'))

        return self.write({'code': 200, 'success': '成功'})

def make_app():
    return tornado.web.Application([
        (r'/getuser', GetUserHandler),
        (r'/getuser2', GetUser2Handler),
        (r'/getmoney', GetMoneyHandler),
        (r'/setmoney', SetMoneyHandler),
        (r'/setmoney2', SetMoney2Handler),
        (r'/uploadfile', UploadFileHandler)
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8081)
    tornado.ioloop.IOLoop.current().start()
