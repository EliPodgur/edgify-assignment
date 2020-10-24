from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import threading
from order import Order
import json

import exec_server

orders = []
executed_orders = []
orders_lock = threading.Lock()
max_connections = 10
semaphore = threading.BoundedSemaphore(max_connections)
condition = threading.Condition(orders_lock)


class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass


class MyServer(BaseHTTPRequestHandler):

    def do_POST(self):
        global executed_orders, orders
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)   # using json more scalable
        price = data['price']
        order_type = data['order']
        new_order = Order(price, order_type)
        with semaphore:  # max 10 threads in this block - wont allow new batch before last is finished
            with condition:
                orders.append(new_order)
                index = len(orders) - 1
                if len(orders) == 10:
                    executed_orders = exec_server.ExecutionSdk.execute_orders(orders) # MOCK; in production replace with POST
                    orders = []
                    condition.notify_all()
                else:
                    condition.wait()
                new_order.status = executed_orders[index].status

        s = f"POST request for price: {price}, order type: {order_type} result: {new_order.status}".encode('utf-8')
        self._set_response()
        self.wfile.write(s)

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()


if __name__ == '__main__':
    server_address = ('', 8080)
    webServer = ThreadingSimpleServer(server_address, MyServer)
    print('Starting webServer')
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    webServer.server_close()
    print('Stopping webServer')

