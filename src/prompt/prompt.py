# -*- coding: utf-8 -*-
class PromptBuilder:
    @staticmethod
    def build_prompt(history: str, context: str, user_message: str) -> str:
        clean_context = context.strip() or "No additional context available."
        return (
            f"Conversation History:\n{history}\n\n"
            f"Relevant Information:\n{clean_context}\n\n"
            f"User Query:\n{user_message}\n\n"
            "Instructions for RamiAI: First, carefully analyze the conversation history and relevant information. "
            "Then, clearly outline your reasoning in distinct steps, addressing each key point. "
            "Finally, provide a single, final answer to the user query without initiating further dialogue. "
            "Do not ask follow-up questions — just deliver a complete, concise, and professional response.\n"
            "RamiAI Answer:"
        )



if __name__ == "__main__":
    # Example usage
    history = "user: Hello Rami how are u?, RamiAI: I'm Fine thatnk you, what u doing?"
    context = "No, retrieved Context"
    user_message = "What is the weather like today?"
    prompt = PromptBuilder.build_prompt(history, context, user_message)
    print(prompt)
