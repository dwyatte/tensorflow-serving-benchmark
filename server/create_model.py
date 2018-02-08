import os
import argparse
import tensorflow as tf

parser = argparse.ArgumentParser()
parser.add_argument('path')
parser.add_argument('--version', default=0)
args = parser.parse_args()

inputs = tf.placeholder(tf.int32, [None, 1])
outputs = tf.identity(inputs)

inputs_info = tf.saved_model.utils.build_tensor_info(inputs)
outputs_info = tf.saved_model.utils.build_tensor_info(outputs)

signature = (
    tf.saved_model.signature_def_utils.build_signature_def(
        inputs={tf.saved_model.signature_constants.PREDICT_INPUTS: inputs_info},
        outputs={tf.saved_model.signature_constants.PREDICT_OUTPUTS: outputs_info},
        method_name=tf.saved_model.signature_constants.PREDICT_METHOD_NAME
    )
)

with tf.Session() as sess:
    builder = tf.saved_model.builder.SavedModelBuilder(os.path.join(args.path, str(args.version)))
    builder.add_meta_graph_and_variables(
        sess,
        [tf.saved_model.tag_constants.SERVING],
        signature_def_map={tf.saved_model.signature_constants.PREDICT_METHOD_NAME: signature}
    )
    builder.save()
