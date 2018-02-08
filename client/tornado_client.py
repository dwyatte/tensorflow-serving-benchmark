import os
import argparse
import grpc
import ujson as json
from tornado.ioloop import IOLoop
from tornado.gen import Future, coroutine
from tornado.web import RequestHandler, Application
from tornado.httpserver import HTTPServer
import numpy as np
import tensorflow as tf
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc

# The following two functions wrap grpc futures in futures that can be yielded
# by Tornado https://github.com/grpc/grpc/wiki/Integration-with-tornado-(python)
def _fwrap(f, gf):
    try:
        f.set_result(gf.result())
    except Exception as e:
        f.set_exception(e)

def fwrap(gf, ioloop=None):
    f = Future()
    if ioloop is None:
        ioloop = IOLoop.current()
    gf.add_done_callback(lambda _: ioloop.add_callback(_fwrap, f, gf))
    return f

class PredictionHandler(RequestHandler):
    def initialize(self, serving_host, serving_port, model_name):
        self.serving_host = serving_host
        self.serving_port = serving_port
        self.model_name = model_name
        self.channel = grpc.insecure_channel('{}:{}'.format(self.serving_host, self.serving_port))
        self.stub = prediction_service_pb2_grpc.PredictionServiceStub(self.channel)

    @coroutine
    def get(self):
        request = predict_pb2.PredictRequest()
        request.model_spec.name = self.model_name
        request.model_spec.signature_name = tf.saved_model.signature_constants.PREDICT_METHOD_NAME
        request.inputs[tf.saved_model.signature_constants.PREDICT_INPUTS].CopyFrom(
            tf.contrib.util.make_tensor_proto([[1]], shape=[1, 1]))

        try:
            result_future = yield fwrap(self.stub.Predict.future(request, 10))
            self.set_status(200)
            response = {'outputs': np.array(result_future.outputs['outputs'].int_val).tolist()}
            self.write(json.dumps(response))
        except grpc.RpcError as e:
            self.set_status(500)


parser = argparse.ArgumentParser()
parser.add_argument('--model_name', default=os.getenv('MODEL_NAME', None))
parser.add_argument('--serving_host', default=os.getenv('SERVING_HOST', None))
parser.add_argument('--serving_port', default=os.getenv('SERVING_PORT', '8500'))
parser.add_argument('--client_port', default=os.getenv('CLIENT_PORT', None))
args = parser.parse_args()

app = Application([
        ('/prediction', PredictionHandler, {'serving_host': args.serving_host,
                                            'serving_port': args.serving_port,
                                            'model_name': args.model_name})
      ])
server = HTTPServer(app)
server.bind(int(args.client_port))
server.start(0)  # forks one process per cpu
IOLoop.current().start()
