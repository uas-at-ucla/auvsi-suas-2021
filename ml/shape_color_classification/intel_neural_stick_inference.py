# Learn more at https://docs.openvino.ai/latest/openvino_docs_IE_DG_Integrate_with_customer_application_new_API.html?sw_type=switcher-python

from openvino.inference_engine import IECore

"""STEP 1: Create the Inference Engine Core"""
ie = IECore()


"""STEP 2: Read model. Configure Input and Output of the Model (Optional)"""
net = ie.read_network(model='./intel_neural_stick/shape_color_classifier_model.xml')

inputs = net.input_info
input_name = next(iter(net.input_info))

outputs = net.outputs
output_name = next(iter(net.outputs))

print("Inputs:")
for name, info in net.input_info.items():
    print("\tname: {}".format(name))
    print("\tshape: {}".format(info.tensor_desc.dims))
    print("\tlayout: {}".format(info.layout))
    print("\tprecision: {}\n".format(info.precision))

print("Outputs:")
for name, info in net.outputs.items():
    print("\tname: {}".format(name))
    print("\tshape: {}".format(info.shape))
    print("\tlayout: {}".format(info.layout))
    print("\tprecision: {}\n".format(info.precision))


"""STEP 3: Load Model to the Device"""
exec_net = ie.load_network(net, 'CPU')


"""STEP 4: Prepare Input"""
import cv2
import numpy as np

image = cv2.imread('./intel_neural_stick/ship-2.jpeg')
image = cv2.resize(image, dsize=(227, 227))
cv2.imshow('input', image)
cv2.waitKey(0)

# Converting image to Batch Size, Channels, Width, Height format with FP32 type
input_data = np.expand_dims(np.transpose(image, (2, 0, 1)), 0).astype(np.float32)

"""STEP 5: Start Inference"""
result = exec_net.infer({input_name: input_data})

"""STEP 6: Process the Inference Results"""
output = result[output_name]
print(output)