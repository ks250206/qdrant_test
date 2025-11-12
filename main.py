from openai import OpenAI
from openai.resources.embeddings import Embeddings
from openai.types.embedding import Embedding
import qdrant_client
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct


def init_qdrant() -> QdrantClient:
    client_qdrant: QdrantClient = qdrant_client.QdrantClient(
        host="localhost", port=6333
    )
    if not client_qdrant.collection_exists("my_collection"):
        client_qdrant.create_collection(
            collection_name="my_collection",
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
        )
    return client_qdrant


def init_embedding_model_openai():
    client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")
    return client.embeddings


def sentences_to_embeddings(model: Embeddings, sentences: list[str]) -> list[Embedding]:
    res = model.create(model="text-embedding-qwen3-embedding-0.6b", input=sentences)
    return res.data


def upsert_sentences_to_qdrant(
    client_qdrant: QdrantClient,
    sentences: list[str],
    data: list[Embedding],
):
    for datum, sentence in zip(data, sentences):
        client_qdrant.upsert(
            collection_name="my_collection",
            points=[
                PointStruct(
                    id=datum.index, vector=datum.embedding, payload={"text": sentence}
                )
            ],
        )


def insert_new_sentence_to_qdrant(
    client_qdrant: QdrantClient,
    sentence: str,
    data: Embedding,
):
    count = client_qdrant.count(collection_name="my_collection").count
    client_qdrant.upsert(
        collection_name="my_collection",
        points=[
            PointStruct(id=count, vector=data.embedding, payload={"text": sentence})
        ],
    )


def main():
    client_qdrant = init_qdrant()
    embedding_model_openai = init_embedding_model_openai()

    sentences = [
        "This is an example sentence",
        "Each sentence is converted",
        "いろはにほへと",
        "あいうえお",
        "かきくけこ",
    ]

    data = sentences_to_embeddings(embedding_model_openai, sentences)
    upsert_sentences_to_qdrant(client_qdrant, sentences, data)
    input_text = input("Enter a text: ")

    data_input_text = sentences_to_embeddings(embedding_model_openai, [input_text])[0]
    embedding_input_text = data_input_text.embedding

    search_results = client_qdrant.search(
        collection_name="my_collection",
        query_vector=embedding_input_text,
        limit=1,
    )
    insert_new_sentence_to_qdrant(client_qdrant, input_text, data_input_text)

    if not search_results:
        print("見つかりません")
        return
    answer = search_results[0]

    print(
        f"最も近いテキスト: {answer.payload.get('text') if answer.payload else '見つかりません'}"
    )
    print(f"最も近いテキストの類似度: {answer.score}")
    print(f"最も近いテキストのID: {answer.id}")
    print(f"最も近いテキストのペイロード: {answer.payload}")


if __name__ == "__main__":
    main()
