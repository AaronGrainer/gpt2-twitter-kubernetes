from transformers import AutoTokenizer, AutoModelForCausalLM, TextDataset, DataCollatorForLanguageModeling
from transformers import TrainingArguments, Trainer

import torch
from torch.utils.data import Dataset, DataLoader

from ml.config import global_config as gc

import os
import pickle
import pandas as pd
from typing import List
import wandb


class GPT2Trainer:
    def __init__(self, model_checkpoint: str, dataset: List):
        """Load class configs

        Args:
            model_checkpoint (str): Huggingface pretrained model name
            dataset (List): Train dataset
        """
        self.device = 'cuda:0' if torch.cuda.is_available() else 'cpu'

        self.model_checkpoint = model_checkpoint
        self.dataset = dataset
        self.checkpoint_path = gc.gpt2_checkpoint_path
        self.model_path = os.path.join(gc.gpt2_checkpoint_path, gc.gpt2_model_torchscript_filename)

        # self.lr = 2e-5
        self.batch_size = 16
        self.epochs = 3
        self.weight_decay = 0.01

        self._load()

    def _load(self):
        """Load Tokenizer, Dataset, Model and Jit input example
        """
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_checkpoint)
        self.data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer, mlm=False,
        )
        self.gpt2_dataset = dict(
            train=TextDataset(tokenizer=self.tokenizer,
                              file_path=self.dataset,
                              block_size=128),
            validation=TextDataset(tokenizer=self.tokenizer,
                                   file_path=self.dataset,
                                   block_size=128)
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_checkpoint,
            torchscript=True
        )

        dataloader = DataLoader(self.gpt2_dataset['train'], batch_size=1, shuffle=True)
        batch_input = next(iter(dataloader))
        self.trace_input = (batch_input.to(self.device))
        
    def train_and_evaluate(self, run_name: str = None):
        """Train and model and evaluate

        Args:
            run_name (str, optional): Name of the Wandb run. Defaults to None.
        """
        wandb.init(project='gpt2-twitter', 
                   name=run_name)

        training_args = TrainingArguments(
            'ml/checkpoint/gpt2-twitter-trainer',
            overwrite_output_dir=True,
            evaluation_strategy='epoch',
            # learning_rate=self.lr,
            per_device_train_batch_size=self.batch_size,
            per_device_eval_batch_size=self.batch_size,
            num_train_epochs=self.epochs,
            weight_decay=self.weight_decay,
            logging_steps=50,
            eval_steps=400,
            save_steps=800,
            save_total_limit=1,
            warmup_steps=500
        )

        trainer = Trainer(
            model=self.model,
            args=training_args,
            data_collator=self.data_collator,
            train_dataset=self.gpt2_dataset['train'],
            eval_dataset=self.gpt2_dataset['validation']
        )

        trainer.train()

        wandb.finish()

    def save(self):
        """Save torchscipt model
        """
        print('Saving torchscript model')
        if not os.path.exists(self.checkpoint_path):
            os.makedirs(self.checkpoint_path)

        self.model.eval()
        traced_model = torch.jit.trace(self.model, self.trace_input)
        torch.jit.save(traced_model, self.model_path)


if __name__ == '__main__':
    run_name = 'gpt2-twitter'
    model_checkpoint = 'gpt2'
    dataset = 'data/karpathy_tweets.txt'

    gpt2_trainer = GPT2Trainer(model_checkpoint=model_checkpoint, dataset=dataset)
    # gpt2_trainer.train_and_evaluate(run_name=run_name)
    gpt2_trainer.save()


