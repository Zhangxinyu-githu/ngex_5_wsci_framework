## This file is a bad way of managing context. 

from pathlib import Path
from ollama import chat


question = """
I changed my university password this morning.
Now my Windows laptop won't connect to campus Wi-Fi,
but my phone still works.
"""


context = ""

for file in Path("knowledge").glob("*.txt"):
    context += file.read_text()
    context += "\n\n"

## Make a call to Qwen with student's question and the context from the knowledge base.
response = chat(
    model="qwen",
    messages=[
        {
            "role": "system",
            "content": "You are a university IT support assistant. Use the provided context to answer the student\'s question. Give a clear, helpful, step-by-step answer."
        },
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {question}"
        }
    ]
)


## Just for fun, print the total length of the context
print(
    "Context characters:",
    len(context)
)

## Print the response from Qwen
print(response.message.content)
