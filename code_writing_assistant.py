from openai import OpenAI
import os
import time

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
 
assistant = client.beta.assistants.retrieve("asst_0qHA1gFaz1PYME8318adcMlY")

## Create a new thread
thread = client.beta.threads.create()
message = client.beta.threads.messages.create(
  thread_id=thread.id,
  role="user",
  #content="Write a function that will extract the nth most recent code block from a markdown file.",
  content="Write a function the will pretty print a calendar of the given month and year."
)

run = client.beta.threads.runs.create(
    assistant_id=assistant.id,
    thread_id=thread.id
)

while run.status != "completed":
    run = client.beta.threads.runs.retrieve(run_id=run.id, thread_id=run.thread_id)
    print(run.status)
    time.sleep(1)

messages = client.beta.threads.messages.list(thread_id=thread.id)
for message in messages:
    print(message.content[0].text.value)
    start = message.content[0].text.value.find("```python") + len("```python")
    end = message.content[0].text.value.find("```", start)
    code_block = message.content[0].text.value[start:end].strip()
    print(code_block)

print("Done.")



