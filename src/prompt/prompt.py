# -*- coding: utf-8 -*-
class PromptBuilder:
    """
    Builds a personalized prompt for RamiAI, the WhatsApp Business chatbot for Rami.
    It includes the system message, conversation history, retrieved context, and the user's question.
    """

    prompt = (
        "You are RamiAI, a helpful and professional assistant for Rami on WhatsApp Business.\n"
        "Use the context and conversation history to respond clearly and concisely.\n\n"
        "### Conversation History:\n"
        "{history}\n\n"
        "### Relevant Context:\n"
        "{retrieved_context}\n\n"
        "### User Question:\n"
        "{query}\n\n"
        "### RamiAI Response:"
    )


if __name__ == "__main__":
    # Example usage
    history = "User: Hi, I need help with my order.\nRamiAI: Sure, can you provide your order number?"
    retrieved_context = "Order number: 12345. Order status: Shipped."
    query = "Can you tell me the status of my order?"

    prompt = PromptBuilder.prompt.format(history=history, retrieved_context=retrieved_context, query=query)
    print(prompt)
