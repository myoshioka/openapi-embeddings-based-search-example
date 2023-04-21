import os
import sys
from os.path import join, dirname
import ast  # for converting embeddings saved as strings back to arrays
import openai  # for calling the OpenAI API
import pandas as pd  # for storing text and embeddings data
import tiktoken  # for counting tokens
from scipy import spatial  # for calculating vector similarities for search
from dotenv import load_dotenv

import pprint

from wikipedia_article import wikipedia_article_on_curling

# models
EMBEDDING_MODEL = "text-embedding-ada-002"
GPT_MODEL = "gpt-3.5-turbo"


def strings_ranked_by_relatedness(
        query: str,
        df: pd.DataFrame,
        relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y),
        top_n: int = 100) -> tuple[list[str], list[float]]:
    """Returns a list of strings and relatednesses, sorted from most related to least."""
    query_embedding_response = openai.Embedding.create(
        model=EMBEDDING_MODEL,
        input=query,
    )
    query_embedding = query_embedding_response["data"][0]["embedding"]
    strings_and_relatednesses = [(row["text"],
                                  relatedness_fn(query_embedding,
                                                 row["embedding"]))
                                 for i, row in df.iterrows()]

    strings_and_relatednesses.sort(key=lambda x: x[1], reverse=True)
    strings, relatednesses = zip(*strings_and_relatednesses)
    return strings[:top_n], relatednesses[:top_n]


def relatedness_data_print():
    df = pd.read_csv('winter_olympics_2022.csv')
    df['embedding'] = df['embedding'].apply(ast.literal_eval)

    strings, relatednesses = strings_ranked_by_relatedness(
        "curling gold medal", df, top_n=5)

    for string, relatedness in zip(strings, relatednesses):
        print(f"{relatedness=:.3f}")
        print(string)


def num_tokens(text: str, model: str = GPT_MODEL) -> int:
    """Return the number of tokens in a string."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def query_message(query: str, df: pd.DataFrame, model: str,
                  token_budget: int) -> str:
    """Return a message for GPT, with relevant source texts pulled from a dataframe."""
    strings, relatednesses = strings_ranked_by_relatedness(query, df)
    introduction = 'Use the below articles on the 2022 Winter Olympics to answer the subsequent question. If the answer cannot be found in the articles, write "I could not find an answer."'
    question = f"\n\nQuestion: {query}"

    message = introduction
    for string in strings:
        next_article = f'\n\nWikipedia article section:\n"""\n{string}\n"""'
        if (num_tokens(message + next_article + question, model=model) >
                token_budget):
            break
        else:
            message += next_article
    return message + question


def ask(
    query: str,
    df: pd.DataFrame,
    model: str = GPT_MODEL,
    token_budget: int = 4096 - 500,
    print_message: bool = False,
) -> str:
    """Answers a query using GPT and a dataframe of relevant texts and embeddings."""
    message = query_message(query, df, model=model, token_budget=token_budget)
    if print_message:
        print(message)

    messages = [
        {
            "role": "system",
            "content": "2022年北京オリンピックについて回答してください"
        },
        {
            "role": "user",
            "content": message
        },
    ]
    response = openai.ChatCompletion.create(model=model,
                                            messages=messages,
                                            temperature=0)
    response_message = response["choices"][0]["message"]["content"]
    return response_message


def main():
    openai.api_key = os.environ["OPENAI_API_KEY"]
    print('start')

    query = '2022年の北京オリンピックで男子スノーボードハーフパイプの金メダルをもらった選手は誰ですか?'
    print(query)

    response = openai.ChatCompletion.create(
        messages=[
            {
                'role': 'system',
                'content': '2022年北京オリンピックについて回答してください'
            },
            {
                'role': 'user',
                'content': query
            },
        ],
        model=GPT_MODEL,
        temperature=0,
    )
    # pprint.pprint(response, width=1, indent=4)
    print(response['choices'][0]['message']['content'])

    df = pd.read_csv('winter_olympics_2022_jp.csv')
    df['embedding'] = df['embedding'].apply(ast.literal_eval)

    result = ask(query, df, print_message=False)
    print(result)


if __name__ == '__main__':
    load_dotenv(join(dirname(__file__), '.env'))

    main()
