# -*- coding: utf-8 -*-
import logging
import tornado.gen
import tornado.web
import tornado.websocket

from tornado.options import define, options, parse_command_line


define('port', default=12123, type=int)

clients = set()

class PingHandler(tornado.web.RequestHandler):
    def get(self):
        self.write({'message': 'ok'})


class CloseHandler(tornado.web.RequestHandler):
    def get(self):
        for client in clients:
            client.close()
        self.write({'message': 'ok'})


class WSHandler(tornado.websocket.WebSocketHandler):

    def check_origin(self, origin):
        logging.info('check origin, origin: %s', origin)
        return True

    def open(self):
        clients.add(self)
        logging.info('open, ip - %s', self.request.remote_ip)

    def on_message(self, message):
        logging.info('on_message - %s', message)

    def on_close(self):
        logging.info('websocket closed')
        clients.remove(self)

    def on_pong(self, data):
        self.pong_receive = True
        logging.info('on_pong data - %s', data)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            ('/ping', PingHandler),
            ('/close', CloseHandler),
            ('/ws', WSHandler),
        ]
        super(Application, self).__init__(handlers)


def main():
    parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
