from transformers import AutoTokenizer, AutoModelForCausalLM

import torch

from ml.config import global_config as gc

import os


class GPT2Inferencer:
    def __init__(self):
        self.username = 'karpathy'

        self.device = 'cuda:0' if torch.cuda.is_available() else 'cpu'

        self.model_path = os.path.join(gc.gpt2_checkpoint_path, gc.gpt2_model_path)
        self.tweet_predicted_path = gc.tweet_predicted_path
        self.tweet_filename = os.path.join(gc.tweet_predicted_path, f'{self.username}__predicted_tweets.txt')

        self.model_checkpoint = 'gpt2'
        self.max_length = 100

        self.start_sequence = '<|startoftext|> '

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

        inputs = self.tokenizer.encode(self.start_sequence, return_tensors='pt')

        outputs = self.gpt2_model.generate(inputs,
                                           do_sample=True,
                                           max_length=200,
                                           top_k=50, 
                                           top_p=0.95, 
                                           num_return_sequences=100)
        tweets = [self.tokenizer.decode(output, skip_special_tokens=True) for output in outputs]

        return tweets

    def save_tweets(self, tweets):
        """Save predicted tweets
        """
        print('Saving predicted tweets')
        if not os.path.exists(self.tweet_predicted_path):
            os.makedirs(self.tweet_predicted_path)

        with open(self.tweet_filename, 'w', encoding="utf-8") as f:
            tweets = [tweet.replace(self.start_sequence, '').strip().capitalize() for tweet in tweets]
            f.write('\n###############\n'.join(tweets))


class ModelNotTrained(Exception):
    pass


if __name__ == '__main__':
    gpt2_inferencer = GPT2Inferencer()
    tweets = gpt2_inferencer.predict()
    print('tweets: ', tweets)
    gpt2_inferencer.save_tweets(tweets)


