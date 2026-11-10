import torch,torchvision,numpy as np,json
from PIL import Image
from torchvision.models.detection import keypointrcnn_resnet50_fpn, KeypointRCNN_ResNet50_FPN_Weights
w=KeypointRCNN_ResNet50_FPN_Weights.DEFAULT; m=keypointrcnn_resnet50_fpn(weights=w).eval()
im=Image.open('/home/user/work/photos/picks/stage-1.jpg').convert('RGB')
x=torchvision.transforms.functional.to_tensor(im)
with torch.no_grad(): o=m([x])[0]
i=int(torch.argmax(o['scores'])); k=o['keypoints'][i][:,:2].numpy().tolist()
names=['nose','leye','reye','lear','rear','lsh','rsh','lel','rel','lwr','rwr','lhip','rhip','lkn','rkn','lan','ran']
d=dict(zip(names,k)); json.dump(d,open('kp.json','w')); print({n:[round(v) for v in d[n]] for n in ['nose','lsh','rsh','lel','rel','lwr','rwr','lhip','rhip']}, o['boxes'][i].tolist())
