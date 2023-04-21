# Sample of using OpenAI GPT API with embeddings

## Overview

- This repository is a sample code based on [openapi's examples pages](https://github.com/openai/openai-cookbook/blob/main/examples/Question_answering_using_embeddings.ipynb)
- The content is the same, but we have made it possible to search in Japanese by using data from the Japanese Wikipedia site.

## Description

- The Embedding dataset is created by retrieving data from the Japanese Wikipedia site. Please refer to the [Openapi site](https://github.com/openai/openai-cookbook/blob/793384ff3bfe30be9479e24ab93ec2a6b4fa9ff8/examples/Embedding_Wikipedia_articles_for_search.ipynb) for details.

## Getting Started

- Install the library with poetry.

```bash
$ poetry  install
```

- Create an env file and set the API key.

```bash
$ touch .env

# Edit env file
OPENAI_API_KEY=****************

```

- Creates a data set. When completed, a csv file of `winter_olympics_2022_jp.csv` will be saved.(It will take a few minutes to complete.)

```bash
$ poetry run python dataset.py
```

- Ask a question with the openapi API. First, the results of the question without embeddings are displayed. Next, the results using the embeddings you created are displayed.

```bash
$ poetry run python main.py
```

- It is displayed like this.The first answer is incorrect; the second is correct.

```
男子スノーボードハーフパイプで金メダルをもらった選手は誰ですか?
2022年北京オリンピックの男子スノーボードハーフパイプで金メダルを獲得した選手は、日本の平岡卓（Taku Hiraoka）選手です。
2022年北京オリンピックの男子スノーボードハーフパイプで金メダルをもらった選手は平野歩夢（日本）です。
```

