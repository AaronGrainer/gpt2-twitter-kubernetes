from argparse import Namespace
import os


global_config = Namespace(**dict(
    gpt2_dataset_path=os.path.join(os.getcwd(), 'data/karpathy_tweets.txt'),
    gpt2_checkpoint_path=os.path.join(os.getcwd(), 'src/ml/checkpoint/'),
    gpt2_model_path='gpt2-model/',
    tweet_predicted_path=os.path.join(os.getcwd(), 'src/ml/output/'),
))


