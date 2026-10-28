import argparse
import json
import os
from call_function import call_function

from call_function import available_functions
from dotenv import load_dotenv
from openai import OpenAI

from prompts import system_prompt


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Code Assistant")
    parser.add_argument("user_prompt", type=str, help="Prompt to send to the LLM")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    load_dotenv()
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY environment variable not set")

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": args.user_prompt},
    ]
    if args.verbose:
        print(f"User prompt: {args.user_prompt}\n")

    for _ in range(20):
        if generate_content(client, messages, args.verbose):
            break
    else:
        print("Loop finished after 20 iterations.")


def generate_content(client: OpenAI, messages: list, verbose: bool) -> bool:
    response = client.chat.completions.create(
        model="openai/gpt-oss-safeguard-20b",
        messages=messages,
        tools=available_functions,
    )
    if not response.usage:
        raise RuntimeError("API response appears to be malformed")

    if verbose:
        print("Prompt tokens:", response.usage.prompt_tokens)
        print("Response tokens:", response.usage.completion_tokens)


    message = response.choices[0].message

    message = response.choices[0].message

    assistant_msg = {"role": "assistant", "content": message.content or ""}
    if message.tool_calls:
        assistant_msg["tool_calls"] = [
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                },
            }
            for tc in message.tool_calls
        ]
    messages.append(assistant_msg)
    if not message.tool_calls:
        print("Response:")
        print(message.content)

        return True

    for tool_call in message.tool_calls:
        if tool_call.type != "function":
            continue
        function_args = json.loads(tool_call.function.arguments or "{}")
        result_message = call_function(tool_call, verbose)
        if not result_message["content"]:
            raise Exception("Error. 'content' is empty")
        elif verbose:
            print(f"-> {result_message['content']}")
        messages.append(result_message)


if __name__ == "__main__":
    main()
