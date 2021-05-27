from transformers import AutoTokenizer

import torch

from ml.config import global_config as gc

import os


class IntentInferencer:
    def __init__(self):
        self.device = 'cuda:0' if torch.cuda.is_available() else 'cpu'

        self.model_path = os.path.join(gc.gpt2_checkpoint_path, gc.gpt2_model_torchscript_filename)

        self.model_checkpoint = 'gpt2'
        self.max_length = 100

        self._initialize()

    def _initialize(self):
        if os.path.exists(self.model_path):
            print('GPT2 torchscript checkpoint found, initializing model...')
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_checkpoint)
            self.gpt2_model = torch.jit.load(self.model_path)
            self.gpt2_model.eval()
        else:
            print("GPT2 torchscript checkpoint not found, please train the model.")
            self.model = None

    def predict(self):
        if not self.gpt2_model: 
            raise ModelNotTrained

        output = self.gpt2_model(output.to(self.device))
        output = self.softmax(output)
        output_idx = torch.argmax(output)
        output = output.flatten().tolist()

        return output


class ModelNotTrained(Exception):
    pass


