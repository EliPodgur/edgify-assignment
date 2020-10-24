import os
import requests
import json
import threading
os.environ['NO_PROXY'] = '127.0.0.1'


def worker(i):
    print(f"thread {i} statred!")
    for j in range(10):
        data1 = {'price': i * 10 + j, 'order': 'buy'}
        r = requests.post('http://127.0.0.1:8080', data=json.dumps(data1))
        status = r.content.decode("utf-8")
        print(status)
    print(f"thread {i} finished!")


def test_orders():
    for i in range(10):
        t = threading.Thread(target=worker, args=(i,))
        t.start()


