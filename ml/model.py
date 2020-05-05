import gpt_2_simple as gpt2
from datetime import datetime
from random import uniform
import fire
import os


class Model:
  def __init__(self, run_name):
    self.run_name = run_name
    self.sess = None

  def train(self, filename, steps):
    if self.sess:
      print("Saved model loaded, no training required")
      return

    self.sess = gpt2.start_tf_sess()
    gpt2.finetune(self.sess,
                  model_dir='ml/models',
                  checkpoint_dir="ml/checkpoint",
                  dataset=filename,
                  model_name="355M",
                  steps=steps,
                  restore_from="fresh",
                  run_name=self.run_name,
                  print_every=10,
                  sample_every=500,
                  save_every=500)

  def load(self):
    try:
      self.sess = gpt2.start_tf_sess()
      gpt2.load_gpt2(self.sess,
                     run_name=self.run_name,
                     checkpoint_dir="ml/checkpoint",
                     model_dir="ml/models")
    except:
      print("Checkpoint doesn't exists")

  def generate(self):
    print("Generating tweet")
    while True:
      text = gpt2.generate(self.sess,
                           checkpoint_dir="ml/checkpoint",
                           model_dir="ml/models",
                           run_name=self.run_name,
                           length=200,
                           temperature=1.0,
                           top_p=0.9,
                           prefix="<|startoftext|>",
                           truncate="<|endoftext|>",
                           include_prefix=False,
                           return_as_list=True)[0]
      
      if (len(text) > 0 and len(text) <= 280 and "<|startoftext|>" not in text):
        break

    return text

  def generate_to_file(self):
    output_file = "gpt2_{}_{:%Y%m%d_%H%M%S}.txt".format(
        self.run_name, datetime.utcnow())
    gpt2.generate_to_file(self.sess,
                          checkpoint_dir="ml/checkpoint",
                          model_dir="ml/models",
                          run_name=self.run_name,
                          destination_path=output_file,
                          length=200,
                          temperature=1.0,
                          top_p=0.9,
                          prefix="<|startoftext|>",
                          truncate="<|endoftext|>",
                          include_prefix=False,
                          nsamples=1000,
                          batch_size=10)

  def download(self):
    if not os.path.exists("ml/models/355M"):
      gpt2.download_gpt2(model_name="355M",
                         model_dir="ml/models")


def train_gpt2(filename="karpathy_tweets.csv", run_name="karpathy_production", steps=2000):
  """Train a tweet generator using GPT-2 by OpenAI
  :param filename: CSV filename for input training
  """
  model = Model(run_name)
  model.download()
  # model.load()
  model.train(filename=filename, steps=steps)
  model.generate_to_file()


if __name__ == "__main__":
  fire.Fire(train_gpt2)
