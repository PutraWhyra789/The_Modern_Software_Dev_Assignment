import os
from dotenv import load_dotenv
from ollama import chat

load_dotenv()

NUM_RUNS_TIMES = 5

# TODO: Fill this in!
YOUR_SYSTEM_PROMPT = """You are a helpful assistant that reverses the letters of words.

To reverse a word, write the letters in reverse order from last to first.

Examples:

Word: cat
Letters: c-a-t
Reversed: t-a-c
Output: tac

Word: stats
Letters: s-t-a-t-s
Reversed: s-t-a-t-s
Output: stats

Word: httpttt
Letters: h-t-t-p-t-t-t
Reversed: t-t-t-p-t-t-h
Output: tttpthh

Word: httpstatus
Letters: h-t-t-p-s-t-a-t-u-s
Reversed: s-u-t-a-t-s-p-t-t-h
Output: sutatsptth

Now reverse the word given by the user. Show your work with the Letters and Reversed steps, then give only the Output on the final line."""

USER_PROMPT = """
Reverse the order of letters in the following word. Only output the reversed word, no other text:

httpstatus
"""


EXPECTED_OUTPUT = "sutatsptth"

def test_your_prompt(system_prompt: str) -> bool:
    """Run the prompt up to NUM_RUNS_TIMES and return True if any output matches EXPECTED_OUTPUT.

    Prints "SUCCESS" when a match is found.
    """
    for idx in range(NUM_RUNS_TIMES):
        print(f"Running test {idx + 1} of {NUM_RUNS_TIMES}")
        response = chat(
            model="mistral-nemo:12b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": USER_PROMPT},
            ],
            options={"temperature": 0.5},
        )
        output_text = response.message.content.strip()
        if output_text.strip() == EXPECTED_OUTPUT.strip():
            print("SUCCESS")
            return True
        else:
            print(f"Expected output: {EXPECTED_OUTPUT}")
            print(f"Actual output: {output_text}")
    return False

if __name__ == "__main__":
    test_your_prompt(YOUR_SYSTEM_PROMPT)
