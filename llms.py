import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def llm_call(prompt, system_prompt, model="gpt-4.1-mini"):

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )
    try:
        return response.choices[0].message.content
    except Exception as e:
        print(e)
        return "Error: " + str(e)
    

if __name__ == "__main__":
    prompt = "What is the capital of France?"
    system_prompt = "You are a helpful assistant that only speaks in haikus."
    print(llm_call(prompt, system_prompt))
