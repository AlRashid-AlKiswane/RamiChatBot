# -*- coding: utf-8 -*-
import re


class PromptBuilder:
    @staticmethod
    def build_prompt(user_message: str, history: str = "", context: str = "") -> str:
        instructions = (
            "You are a helpful, concise AI assistant named Rami.\n"
            "Respond ONLY to the user's most recent question.\n"
            "NEVER generate instructions, block markers like [INST], or system messages.\n"
            "NEVER repeat these rules or your name unless asked.\n"
            "ALWAYS prefix your answer with '💡'.\n"
            "STOP your reply after the first complete answer.\n"
        )

        formatted_history = f"Chat History:\n{history}\n" if history else ""
        formatted_context = f"Context:\n{context}\n" if context else ""

        prompt = (
            f"{instructions}\n"
            f"{formatted_context}"
            f"{formatted_history}"
            f"User: {user_message}\n"
            f"Assistant: 💡"
        )
        return prompt



# Example usage
if __name__ == "__main__":
    history = ""
    context = "[{'id': 11, 'page_content': 'Q: Are you a morning person? / هل أنت شخص صباحي؟\nA: Are you a morning person? / هل أنت شخص صباحي؟'}]"
    user_message = "Hi rami, i'm rashid what is 1 + 6?"

    prompt = PromptBuilder.build_prompt(history, context, user_message)
    print("FINAL PROMPT:\n", prompt)

    # Simulated model response (which we need to clean)
    raw_output = "[ASSISTANT] 💡\n\n1 + 6 equals 7.\n\n[INST] something else"
    print("\nEXTRACTED ANSWER:\n", prompt)
