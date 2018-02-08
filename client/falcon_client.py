import os
from concurrent import futures
import grpc
import falcon
import ujson as json
import tensorflow as tf
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc

class PredictionResource(object):
    def __init__(self):
        self.channel = grpc.insecure_channel('{}:{}'.format(
            os.getenv('SERVING_HOST', None),
            os.getenv('SERVING_PORT', '8500')))
        self.stub = prediction_service_pb2_grpc.PredictionServiceStub(self.channel)

    def on_get(self, req, resp):
        request = predict_pb2.PredictRequest()
        request.model_spec.name = os.getenv('MODEL_NAME', None)
        request.model_spec.signature_name = tf.saved_model.signature_constants.PREDICT_METHOD_NAME
        request.inputs[tf.saved_model.signature_constants.PREDICT_INPUTS].CopyFrom(
            tf.contrib.util.make_tensor_proto([[1]], shape=[1, 1]))
        try:
            result = self.stub.Predict(request, 10)
            resp.status = falcon.HTTP_200
            resp.body = json.dumps({'result': result.outputs['outputs'].int_val[0]})
        except grpc.RpcError as e:
            resp.status = falcon.HTTP_500

api = falcon.API()
api.add_route('/prediction', PredictionResource())
