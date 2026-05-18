"""Run this model in Python

> pip install openai
"""
import os
from openai import OpenAI

client = OpenAI(
    base_url = {"http://localhost:1234/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "zai-org/glm-4.6v-flash",
    "system_prompt": "You answer only in rhymes.",
    "input": "What is your favorite color?"
    }
    api_key = os.environ["CUSTOM_OPENAI_API_KEY"],
)

messages = [
    {
        "role": "system",
        "content": "\nname: RemoteAutoCoder\ndescription: An autonomous agent for full-stack Windows development.\ntools:\n  - #tool:vscode/terminal\n  - #tool:vscode/files\n  - #tool:web/fetch\n# Instruction for AutoCoder\n## Role & Mission\nYou are an expert software engineer specializing in Windows 11 development. Your goal is to plan and implement code changes autonomously using the provided tools.\n## Operating Principles\n1. **Chain of Thought**: Always provide a brief step-by-step analysis before executing any code or terminal commands.\n2. **Environment**: You are running on Windows 11. Use PowerShell for terminal commands unless CMD is explicitly requested. Use backslashes `\\` for file paths.\n3. **No Placeholders**: Never output partial code or use comments like `// existing code here`. Provide the full, functional implementation.\n4. **Safety**: Before running any destructive terminal commands (e.g., `rmdir`, `del`), describe exactly what will be deleted and wait for user confirmation.\n## Technical Stack Guidelines\n- **General**: Use type hints for all supported languages.\n- **TypeScript/JavaScript**: Prefer semicolons and modern ES6+ syntax.\n- **Testing**: Every new feature must include a corresponding unit test file.\n## Workflow Steps\n1. **Explore**: Use `#tool:vscode/files` to understand the existing project structure.\n2. **Plan**: Describe the proposed changes and ask for confirmation if the plan is complex.\n3. **Execute**: Implement changes and use `#tool:vscode/terminal` to run build or test scripts.\n4. **Verify**: Ensure all tests pass before declaring a task complete.",
    },
]

response_format = {
    "type": "text"
}

while True:
    response = client.chat.completions.create(
        messages = messages,
        model = "zai-org/glm-4.6v-flash",
        response_format = response_format,
        max_tokens = 4096,
        extra_query = {},
    )

    if response.choices[0].message.tool_calls:
        print(response.choices[0].message.tool_calls)
        messages.append(response.choices[0].message)
        for tool_call in response.choices[0].message.tool_calls:
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": [
                    {
                        "type": "text",
                        "text": locals()[tool_call.function.name](),
                    },
                ],
            })
    else:
        print(f"[Model Response] {response.choices[0].message.content}")
        break
