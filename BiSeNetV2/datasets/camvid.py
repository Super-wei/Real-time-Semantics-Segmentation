import numpy as np
import pandas as pd
import cv2
from glob import glob
import torch
from torch.utils.data import Dataset
import torchvision.transforms as transforms


class CamVidDataset(Dataset):
    def __init__(self,
                 path,
                 class_path,
                 subset='train',
                 transform_=None,
                ):
                
        assert subset in ('train', 'valid', 'test')
        self.image_files = glob(path+subset+'/'+subset+'_images/*.png')
        self.label_files = glob(path+subset+'/'+subset+'_labels/*.png')
        class_map = pd.read_csv(class_path, index_col=0)
        self.rgb_class = {name:list(class_map.loc[name, :][:3]) for name in class_map.index}
        self.subset = subset
        self.transform_ = transform_
        self.totensor = transforms.Compose([transforms.ToTensor()])
        
    def __len__(self):
        return len(self.image_files)
    
    def __getitem__(self, idx):
        images = cv2.cvtColor(
            cv2.imread(self.image_files[idx], cv2.IMREAD_COLOR), 
            cv2.COLOR_BGR2RGB
        )
        labels = cv2.cvtColor(
            cv2.imread(self.label_files[idx], cv2.IMREAD_COLOR),
            cv2.COLOR_BGR2RGB
        )
        if self.transform_ is not None:
            augmented = self.transform_(image=images, mask=labels)
            images = augmented['image']
            labels = augmented['mask']
        return self.totensor(images), self.totensor(self.one_hot_encoding(labels))
    
    def one_hot_encoding(self, labels):
        semantic_map = []
        for color in list(self.rgb_data.values()):
            equality = np.equal(labels, color)
            class_map = np.all(equality, axis=-1)
            semantic_map.append(class_map)
        semantic_map = np.stack(semantic_map, axis=-1)
        return np.float32(semantic_map)