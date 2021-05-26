from argparse import Namespace
import os


global_config = Namespace(**dict(
    gpt2_dataset_path=os.path.join(os.getcwd(), 'data/karpathy_tweets.txt'),
    gpt2_checkpoint_path=os.path.join(os.getcwd(), 'ml/checkpoint/'),
    gpt2_model_torchscript_filename='gpt2-twitter-model.pt'
))


