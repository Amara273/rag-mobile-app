import ollama

response = ollama.embed(
    model = "bge-m3",
    input = "ជំងឺកាមរោគមានលក្ខណៈឯកជនភាព។"
)

print(response.embeddings)