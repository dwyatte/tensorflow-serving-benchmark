import os
import time
import argparse
import threading
import grpc
import tensorflow as tf
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc

class Benchmark(object):
    """
    num_requests: Number of requests.
    max_concurrent: Maximum number of concurrent requests.
    """

    def __init__(self, num_requests, max_concurrent):
        self._num_requests = num_requests
        self._max_concurrent = max_concurrent
        self._done = 0
        self._active = 0
        self._condition = threading.Condition()

    def inc_done(self):
        with self._condition:
            self._done += 1
            self._condition.notify()

    def dec_active(self):
        with self._condition:
            self._active -= 1
            self._condition.notify()

    def throttle(self):
        with self._condition:
            while self._active == self._max_concurrent:
                self._condition.wait()
            self._active += 1

    def wait(self):
        with self._condition:
            while self._done < self._num_requests:
                self._condition.wait()


def _create_rpc_callback(benchmark):
    def _callback(result_future):
        exception = result_future.exception()
        if exception:
            print(exception)
        else:
            result = result_future.result().outputs['outputs'].int_val
        benchmark.inc_done()
        benchmark.dec_active()
    return _callback

parser = argparse.ArgumentParser()
parser.add_argument('--model_name', default=os.getenv('MODEL_NAME', None))
parser.add_argument('--serving_host', default=os.getenv('SERVING_HOST', None))
parser.add_argument('--serving_port', default=os.getenv('SERVING_PORT', '8500'))
parser.add_argument('--num_requests', default=1000)
parser.add_argument('--max_concurrent', default=1)
args = parser.parse_args()

channel = grpc.insecure_channel('{}:{}'.format(args.serving_host, args.serving_port))
stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)
benchmark = Benchmark(int(args.num_requests), int(args.max_concurrent))

start_time = time.time()

for i in range(int(args.num_requests)):
    request = predict_pb2.PredictRequest()
    request.model_spec.name = args.model_name
    request.model_spec.signature_name = tf.saved_model.signature_constants.PREDICT_METHOD_NAME
    request.inputs[tf.saved_model.signature_constants.PREDICT_INPUTS].CopyFrom(
        tf.contrib.util.make_tensor_proto([[i % 2**32]], shape=[1, 1]))
    benchmark.throttle()
    result = stub.Predict.future(request, 10)
    result.add_done_callback(_create_rpc_callback(benchmark))

benchmark.wait()
end_time = time.time()

print()
print('{} requests ({} max concurrent)'.format(args.num_requests, args.max_concurrent))
print('{} requests/second'.format(int(args.num_requests)/(end_time-start_time)))
