from ollama import AsyncClient
from chromadb import Collection

EMBED_MODEL = "nomic-embed-text"
EMBED_LEN = 386
EMBED_DEPTH = EMBED_LEN * 10
MAX_RESULTS = 24

async def create_embeddings(client: AsyncClient, collection: Collection, id: str, source: str):
    for index in range(0, min(EMBED_DEPTH, len(source)), EMBED_LEN):
        chunk = f"id: {id}; source: " + source[index:index + EMBED_LEN]
        embed = await client.embed(
            model=EMBED_MODEL,
            input=chunk,
        )
        
        collection.add(
            ids=[id + str(index)],
            embeddings=embed.embeddings[0],
            documents=[chunk],
        )


async def search(client: AsyncClient, collection: Collection, query: str) -> list[str]:
    query = await client.embed(
        model=EMBED_MODEL,
        input=query,
    )
    
    results = collection.query(
        query_embeddings=query["embeddings"],
        n_results=min(collection.count(), MAX_RESULTS)
    )
    
    return results["documents"][0]
