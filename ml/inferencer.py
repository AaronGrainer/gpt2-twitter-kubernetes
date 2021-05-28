from transformers import AutoTokenizer, AutoModelForCausalLM

import torch

from ml.config import global_config as gc

import os


class GPT2Inferencer:
    def __init__(self):
        self.device = 'cuda:0' if torch.cuda.is_available() else 'cpu'

        self.model_path = os.path.join(gc.gpt2_checkpoint_path, gc.gpt2_model_path)

        self.model_checkpoint = 'gpt2'
        self.max_length = 100

        self._initialize()

    def _initialize(self):
        if os.path.exists(self.model_path):
            print('GPT2 checkpoint found, initializing model...')
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_checkpoint)
            self.gpt2_model = AutoModelForCausalLM.from_pretrained(self.model_path)
        else:
            print("GPT2 checkpoint not found, please train the model.")
            self.model = None

    def predict(self):
        if not self.gpt2_model: 
            raise ModelNotTrained

        sequence = 'He began his premiership by forming a five-man war cabinet which included Chamerlain as Lord President of the Council, Labour leader Clement Attlee as Lord Privy Seal (later as Deputy Prime Minister), Halifax as Foreign Secretary and Labour\'s Arthur Greenwood as a minister without portfolio. In practice,'
        inputs = self.tokenizer.encode(sequence, return_tensors='pt')

        outputs = self.gpt2_model.generate(inputs, max_length=200, do_sample=True)
        text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        return text


class ModelNotTrained(Exception):
    pass


if __name__ == '__main__':
    gpt2_inferencer = GPT2Inferencer()
    text = gpt2_inferencer.predict()
    print('text: ', text)


