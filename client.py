# -*- coding: utf-8 -*-
import time
import logging
from datetime import timedelta


from tornado import gen, ioloop
from tornado.websocket import websocket_connect

RETRY_INTERVAL = 0.5
SERVER_HOST = '127.0.0.1:12123'


@gen.coroutine
def main():
    connection_url = 'ws://{}/ws'.format(SERVER_HOST)
    conn = yield websocket_connect(connection_url)
    logging.info(' **** OK connect %s ****', connection_url)
    while True:
        rm = conn.read_message()
        while True:
            try:
                message = yield gen.with_timeout(timedelta(seconds=5), rm)
                logging.info(' === recerive - %s ===', message)
                if message is None:
                    return
            except gen.TimeoutError:
                conn.write_message('ok')


if __name__ == '__main__':
    FORMAT = '%(asctime)-15s - %(message)s'
    level = logging.INFO
    logging.basicConfig(format=FORMAT, level=level)
    io_loop = ioloop.IOLoop.current()

    retry_count = 0
    interval = RETRY_INTERVAL

    while True:
        try:
            start = time.time()
            io_loop.run_sync(main)
            logging.info('io loop end')
        except ConnectionRefusedError:
            pass
        except KeyboardInterrupt:
            break
        except:
            logging.info('', exc_info=True)

        if time.time() - start < 1:
            if interval < 3:
                interval = min(interval * 1.1, 3)
            retry_count += 1
            logging.info('The %s retry, sleep %s s', retry_count, interval)

            time.sleep(interval)
        else:
            interval = RETRY_INTERVAL
            retry_count = 0
