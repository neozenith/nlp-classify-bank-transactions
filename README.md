# NLP Experiments: How much do I spend on groceries?

What started as an intro to learning SpaCy has turned into a comparison of text classification methods on my bank transactions.

Not happy with how my bank was attempting to classify transactions I thought I'd do it myself. I want to classify my transactions to figure out how much we spend on groceries. It is a variable amount at a variable frequency. So the only signal we have is the transaction description which is also quite variable as we grocery shop at the closest shopping centre relative to where we may be heading for other errands so these descriptions change over time too.

Turns out this is quite hard since bank transactions aren't full sentences, have very little context, words often aren't full words but concatenations of abbreviated words.

 - So existing language models are useless.
 - Word2vec has a lot of Out Of Vocabulary (OOV) issues
 - Keyword matching on vocab seems to be useful.
 - Similar subwords should be predictors even when concatenated with a brand; eg "chemist", "chem", "pharmacy", "pharma", "pharm"

So I want to try and build a classifier, that uses word2vec to approximate similar words into concept vectors, but the subword vectors can help approximate those words in something like "PRICELINEPHARAMA".

fastText has made a lot of progress in this space, but SpaCy has forked fastText and created floret for subword embeddings.

## Getting started

Download example data into `data/`

Then setup your dev environment:

```bash
python3 tasks.py init && . ./.venv/bin/activate
invoke lab
```

This will open `jupyter-lab` where experiments can be found in [`notebooks/`](/notebooks/)

## Project Lifecycle Tasks

```
 inv --list
Available tasks:

  format    Autoformat code, notebooks and sort imports.
  lint      Linting and fomatting checks for quality control.
  test      Run test suite with dependency on lint task running first.
  lab       Launch jupyter lab instance.
  publish   Clean, format and run all notebooks.
```

## TODO

 - fastText academic papers
    - Enriching Word Vectors with Subword Information https://arxiv.org/abs/1607.04606
    - Bag of Tricks for Efficient Text Classification https://arxiv.org/abs/1607.01759

 - spacy/floret subword vectors
    - https://explosion.ai/blog/spacy-v3-2#floret

 - Visualise word/subword embeddings of transaction vocab to verify similarity of fragment words
    - Use t-SNE for dimension reduction of word vectors?

 - LIME and SHAP explanations of models
    - https://github.com/practical-nlp/practical-nlp-code/blob/master/Ch4/08_LimeDemo.ipynb
    - https://github.com/practical-nlp/practical-nlp-code/blob/master/Ch4/10_ShapDemo.ipynb

# References:

 - https://www.oreilly.com/library/view/applied-natural-language/9781492062561/
 - https://www.oreilly.com/library/view/mastering-spacy/9781800563353/
 - https://www.oreilly.com/library/view/practical-natural-language/9781492054047/
 - https://www.oreilly.com/library/view/natural-language-processing/9781098103231/
