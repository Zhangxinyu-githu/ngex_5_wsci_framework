from pathlib import Path
from ollama import chat
import json



question = """
I changed my university password this morning.
Now my Windows laptop won't connect to campus Wi-Fi,
but my phone still works.
"""

## WRITE ##
service_status = {
    "wifi": "operational"
}

state = {
    "problem": question,
    "wi_fi status": "operational",
    "wi-fi_check": True
}

with open("state.json", "w") as file:
    json.dump(
        state,
        file,
        indent=2
    )

with open("state.json", "r") as file:
    state = json.load(file)

print(state)


## SELECT CONTEXT FILES BASED ON QUESTION
## Create the function that takes the student's question, takes some keywords and chooses the relevant files from the knowledge base. Return a list of the selected files.
## For example, if the question has the kyeword "print" or "printer", then the function should return the file "knowledge/printer_setup.txt" in a list.
def select_context(question):
    question_lower = question.lower()
    keyword_map = {
        "password": ["knowledge/password_changes.txt"],
        "wifi": ["knowledge/wifi_setup.txt"],
        "wi-fi": ["knowledge/wifi_setup.txt"],
        "eduroam": ["knowledge/wifi_setup.txt"],
        "network": ["knowledge/wifi_setup.txt"],
        "print": ["knowledge/printing.txt"],
        "printer": ["knowledge/printing.txt"],
        "vpn": ["knowledge/vpn.txt"],
        "projector": ["knowledge/classroom_projectors.txt"],
        "display": ["knowledge/classroom_projectors.txt"],
        "service": ["knowledge/service_status.txt"],
        "status": ["knowledge/service_status.txt"],
        "operational": ["knowledge/service_status.txt"],
    }
    
    selected = []
    for keyword, files in keyword_map.items():
        if keyword in question_lower:
            selected.extend(files)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_selected = []
    for f in selected:
        if f not in seen:
            seen.add(f)
            unique_selected.append(f)
    
    return unique_selected


selected_files = select_context(question)

## READ SELECTED FILES and add their contents to the context variable.
context = ""
for file_path in selected_files:
    context += Path(file_path).read_text()
    context += "\n\n"

## 
## COMPRESS CONTEXT
## Add logic to compress the context from above by calling Qwen with "context" and the "question" as the parameter
## The response from Qwen should be the compressed context. Store it in a variable called "compressed_context" 

def compress_context(context, question):
    response = chat(
            model="qwen",
            messages=[
                {
                    "role": "system",
                    "content": "You are a context compression assistant. Extract only the most relevant information from the context that relates to the user's question. Output only the compressed text, nothing else."
                },
                {
                    "role": "user",
                    "content": f"Question: {question}\n\nContext: {context}\n\nPlease compress the context to only include information relevant to the question. Output only the compressed context text."
                }
            ]
        )
    return response.message.content


compressed_context = compress_context(context, question)
## Print the length of the compressed context
print(len(compressed_context))

## Now, call Qwen again with the compressed context and the student's question. Store the response in a variable called "response" and print the response from Qwen.
## Ensure the model produces a structured output 
response = chat(
    model="qwen",
    messages=[
        {
            "role": "system",
            "content": "You are a university IT support assistant. Use the compressed context to answer the student's question. Provide a clear, helpful, and structured response with actionable steps."
        },
        {
            "role": "user",
            "content": f"Compressed Context:\n{compressed_context}\n\nQuestion: {question}"
        }
    ]
)




print(response.message.content)

## WRITE the above output in an artifact called "state"

## Update the rest of the code so that it uses the "state" artifact as part of the context. 
## It is important to ensure that the model uses only the relevant parts from the "state" artifact and not the entire artifact.
## For this, you may have to think of a good structure for the "state" artifact and how to use it in the context.
state["response"] = response.message.content
state["compressed_context"] = compressed_context
state["selected_files"] = selected_files

with open("state.json", "w") as file:
    json.dump(state, file, indent=2)

with open("state.json", "r") as file:
    state = json.load(file)

problem_text = state["problem"]
wifi_status = state.get("wi_fi status", "unknown")
wifi_check = state.get("wi-fi_check", False)
compressed_txt = state.get("compressed_context", "")

final_context = (
    f"Problem: {problem_text}\n"
    f"Service Status: {wifi_status}\n"
    f"Wi-Fi Check: {wifi_check}\n"
    f"Compressed Context: {compressed_txt}\n"
)

final_response = chat(
    model="qwen",
    messages=[
        {
            "role": "system",
            "content": "You are a university IT support assistant. Use the state information above to provide a final answer to the student's question. Structure your response with: 1) Problem summary, 2) Root cause, 3) Step-by-step solution, 4) Prevention tips."
        },
        {
            "role": "user",
            "content": f"State Context:\n{final_context}\n\nQuestion: {problem_text}"
        }
    ]
)

print("\n=== Final Response (using state artifact) ===")
print(final_response.message.content)


