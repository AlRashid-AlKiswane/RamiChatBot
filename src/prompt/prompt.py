# -*- coding: utf-8 -*-
import re

class PromptBuilder:
    @staticmethod
    def build_prompt(user_message: str, history: str = "", context: str = "") -> str:
        """
        Constructs a structured prompt for the chatbot based on user input, conversation history, and context.

        :param user_message: The latest message from the user.
        :param history: Previous conversation history to maintain context.
        :param context: Additional relevant information for better responses.
        :return: A well-structured prompt string.
        """
        prompt = "You are an AI assistant representing Rami Issa, the retail sales manager at Gulf Insurance Company.\n"
        prompt += "Your goal is to provide professional and accurate insurance-related information to customers.\n\n"

        if context:
            prompt += f"Context: {context}\n\n"

        if history:
            prompt += f"Conversation History:\n{history}\n\n"

        prompt += f"User Message: {user_message}\n\n"
        prompt += "Respond professionally, clearly, and helpfully."
        prompt += "\nAnswer:"

        return prompt
