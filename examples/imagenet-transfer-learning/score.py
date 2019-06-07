import json
import numpy as np
import os
import tensorflow as tf

def read_tensor_from_byte_array(byteArray,
                                input_height=224,
                                input_width=224,
                                input_mean=127.5,
                                input_std=127.5):
  input_name = "file_reader"
  output_name = "normalized"
  image_reader = tf.image.decode_image(byteArray,channels=3)
  float_caster = tf.cast(image_reader, tf.float32)
  dims_expander = tf.expand_dims(float_caster, 0)
  resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
  normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
  sess = tf.Session()
  result = sess.run(normalized)

  return result

def load_labels(label_file):
  label = []
  proto_as_ascii_lines = tf.gfile.GFile(label_file).readlines()
  for l in proto_as_ascii_lines:
    label.append(l.rstrip())
  return label

def load_graph(model_file):
  graph = tf.Graph()
  graph_def = tf.GraphDef()

  with open(model_file, "rb") as f:
    graph_def.ParseFromString(f.read())
  with graph.as_default():
    tf.import_graph_def(graph_def)

  return graph

def label_image(data):
    t = read_tensor_from_byte_array(data)
    input_name = "import/" + input_layer
    output_name = "import/" + output_layer
    input_operation = graph.get_operation_by_name(input_name)
    output_operation = graph.get_operation_by_name(output_name)

    with tf.Session(graph=graph) as sess:
        results = sess.run(output_operation.outputs[0], {
            input_operation.outputs[0]: t
        })
    results = np.squeeze(results)

    top_k = results.argsort()[-3:][::-1]
    
    return [{labels[i]:str(results[i])} for i in top_k]

from azureml.core.model import Model
from azureml.contrib.services.aml_request  import AMLRequest, rawhttp
from azureml.contrib.services.aml_response import AMLResponse

localmode = False

def init():
    model_path=''
    with open('model.json','r') as f:
        model = json.load(f)
        model_path = Model.get_model_path(model['model_name'])
    global input_layer, output_layer, graph, labels
    if localmode:
        model_path = os.path.join(model_path,'model')
    model_file = os.path.join(model_path,"retrained_graph.pb")
    graph = load_graph(model_file)
    label_file = os.path.join(model_path,"output_labels.txt")
    labels = load_labels(label_file)
    input_layer = "input"
    output_layer = "final_result"
    
@rawhttp
def run(request):
    print("This is run()")
    print("Request: [{0}]".format(request))
    if request.method == 'GET':
        respBody = str.encode(request.full_path)
        return AMLResponse(respBody, 200)
    elif request.method == 'POST':
        data = request.get_data(False)
        print("Data Length:[{}]".format(len(data)))
        labels = label_image(data)
        print("Labels:[{}]".format(json.dumps(labels)))
        respBody = json.dumps(labels)
        return AMLResponse(respBody,200,json_str=True)
    else:
        return AMLResponse("bad request", 500)


if __name__ == "__main__":
  localmode = True
  model_name=''
  with open('model.json','r') as f:
    model = json.load(f)
    model_name = model['model_name']
  try:
      Model.get_model_path(model_name)
  except:
      from azureml.core import Workspace
      ws = Workspace.from_config()
      Model(ws, model_name).download(model_name)

  init()
  file_name = "test-image/tulip.jpg"

  with open(file_name, "rb") as binary_file:
    data = binary_file.read()
    print("Data Length:[{}]".format(len(data)))
    result = label_image(data)
    print(json.dumps(result))


