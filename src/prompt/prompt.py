# -*- coding: utf-8 -*-
class PromptBuilder:
    @staticmethod
    def build_prompt(history: str, context: str, user_message: str) -> str:
        clean_context = context.strip() or "No additional context available."
        return (
        f"Conversation History:\n{history}\n\n"
        f"Relevant Context:\n{clean_context}\n\n"
        f"User Query:\n{user_message}\n\n"
        "RamiAI Instructions:\n"
        "1. Carefully read the entire conversation history to extract any facts, names, or preferences added by the user.\n"
        "2. Use the relevant context provided to enrich your understanding and support your reasoning.\n"
        "3. Clearly outline your thought process in concise steps. Be factual, logical, and comprehensive.\n"
        "4. Answer the user query *directly and professionally* based only on the information available.\n"
        "5. **Don't ask any follow-up questions or start a new dialogue.**\n"
        "6. If the user query relates to previous input (e.g., 'What is my name?'), retrieve that information from the conversation history.\n\n"
        "7. Your answer must be Be short and concise, do not talk too much, and answer according to the question.\n"
        "<|ASSIST|>\n"
        "The answer:\n"
        )


if __name__ == "__main__":
    # Example usage
    history = "user: Hello Rami how are u?, RamiAI: I'm Fine thatnk you, what u doing?"
    context = "No, retrieved Context"
    user_message = "What is the weather like today?"
    prompt = PromptBuilder.build_prompt(history, context, user_message)
    print(prompt)
