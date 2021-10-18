import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

from tqdm import tqdm

from .glo import SampleGenerator


class Validator():
    
    def __init__(self, model, val_loader, loss_func, optimizer):
        self.model = model
        self.val_loader = val_loader
        self.loss_func = loss_func
        self.optimizer = optimizer
        
    def validate(self, min_loss, z):
        # Never set model to eval mode, it requires gradients!!!
        running_loss = []
        for idx, img, _ in tqdm(self.val_loader, leave=False):
            # import ipdb; ipdb.set_trace()
            bs = len(idx)
            loss = torch.full(size=(bs, ), fill_value=min_loss+1.0)
            while torch.any(min_loss < loss):
                self.optimizer.zero_grad()
                preds = self.model(z[idx])
                loss = self.loss_func(preds, img)
                loss.backward()
                self.optimizer.step()
                with torch.no_grad():
                    z[idx] = SampleGenerator.reproject_to_unit_ball(z[idx])
                    
            running_loss.append(loss.mean().item())
            
        return z, np.mean(running_loss)
        