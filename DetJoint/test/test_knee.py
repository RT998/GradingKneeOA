# -*- coding: utf-8 -*-

import os, sys, pdb
import torch
import torchvision.transforms as standard_transforms
import argparse
from torch.utils import data

FILE_PATH = os.path.abspath(__file__)
PRJ_PATH = os.path.dirname(os.path.dirname(FILE_PATH))
sys.path.append(PRJ_PATH)

from yolo_v2.proj_utils.local_utils import mkdirs
from yolo_v2.cfgs.config_knee import cfg
from yolo_v2.darknet import Darknet19
from yolo_v2.datasets.knee import Knee
from yolo_v2.test_yolo import test_eng


def set_args():
    parser = argparse.ArgumentParser(description = 'Testing code for Knee Bone KL prediction')
    parser.add_argument('--batch-size',      type=int, default=1)
    parser.add_argument('--device-id',       type=int, default=1)
    parser.add_argument('--model-name',      type=str, default="kl-det-1654-0.9952.pth")
    parser.add_argument('--model-dir',       type=str, default="best_det")
    # parser.add_argument('--model-name',      type=str, default="")
    args = parser.parse_args()

    return args

if  __name__ == '__main__':
    # Config arguments
    args = set_args()

    # Setting model, testing data and result path
    data_root = "../data/"
    model_root = os.path.join(data_root, args.model_dir)
    save_root =  os.path.join(data_root, "results")
    # mkdirs(save_root, erase=True)

    # Dataloader setting
    input_transform = standard_transforms.Compose([
        standard_transforms.ToTensor(),
        standard_transforms.Normalize([0.5]*3, [0.5]*3)])
    dataset = Knee(data_root, "testing", transform=input_transform)
    dataloader = data.DataLoader(dataset, batch_size=args.batch_size)
    # Set Darknet
    net = Darknet19(cfg)

    cuda_avail = torch.cuda.is_available()
    if cuda_avail:
        print("CUDA {} in use".format(args.device_id))
        net.cuda(args.device_id)
        import torch.backends.cudnn as cudnn
        cudnn.benchmark = True
    else:
        print("CPU mode.")

    print('>> START testing ')
    if args.model_name == "":
        model_names = sorted([name for name in os.listdir(model_root) if name.endswith(".pth")])
        for cur_name in model_names:
            args.model_name = cur_name
            test_eng(dataloader, model_root, save_root, net, args, cfg)
    else:
        model_root = os.path.join(data_root, args.model_dir)
        test_eng(dataloader, model_root, save_root, net, args, cfg)