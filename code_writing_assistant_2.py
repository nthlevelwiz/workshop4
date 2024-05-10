from openai import OpenAI
import time, json
client = OpenAI()

assistant = client.beta.assistants.retrieve("asst_Roz9QmJSIyIG9puSALUC7nWH")

## create a new thread
thread = client.beta.threads.create()

message = client.beta.threads.messages.create(
  thread_id=thread.id,
  role="user",
  content="use a tool to read 'another_calendar_printer.py, and return the contents of the file verbatim, no more and no less than exactly what is in the file."
)


run = client.beta.threads.runs.create(
    assistant_id=assistant.id,
    thread_id=thread.id
)

while run.status != "completed":
    run = client.beta.threads.runs.retrieve(run.id, thread_id=thread.id)
    if run.usage: print(run.usage)
    if run.status == "requires_action":
        ## handle tool calls
        # Define the list to store tool outputs
        tool_outputs = []
        
        # Loop through each tool in the required action section
        for tool in run.required_action.submit_tool_outputs.tool_calls:
            if tool.function.name == "write_file":
                print(tool.function.arguments)
                args = json.loads(tool.function.arguments)
                filename = args.get("filename")
                nth_code_block = 0
                ## get the most recent code block from the messages object
                messages = client.beta.threads.messages.list(
                    thread_id=thread.id
                )
                all_text = ""
                for message in messages:
                    print(message.content[0].text)
                    all_text += str(message.content[0].text.value)
                code_blocks = all_text.split('```')
                code_blocks = code_blocks[-2::-2]
                if len(code_blocks) > nth_code_block:
                    ## write the code block to the file
                    with open(filename, 'w') as file:
                        ## remove the first line in the code block
                        code_blocks[nth_code_block] = code_blocks[nth_code_block].split("\n", 1)[1]
                        file.write(code_blocks[nth_code_block])
                
                tool_outputs.append(
                    {
                        "tool_call_id": tool.id,
                        "output": filename
                    }
                )
            if tool.function.name == "read_file":
                print(tool.function.arguments)
                args = json.loads(tool.function.arguments)
                filename = args.get("filename")
                nth_code_block = args.get("n") or 0
                file_contents = ""
                with open(filename, "r") as file:
                    file_contents = file.read()
                tool_outputs.append(
                    {
                        "tool_call_id": tool.id,
                        "output": file_contents
                    }
                )
        
        ## submit the tool outputs
        client.beta.threads.runs.submit_tool_outputs(
            run.id,
            thread_id=thread.id,
            tool_outputs=tool_outputs
        )
                
                    
        
    

print("done.")
messages = client.beta.threads.messages.list(
    thread_id=thread.id
  )
for message in messages:
    print(message.content[0].text.value)