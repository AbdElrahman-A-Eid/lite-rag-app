"""
Retrieval-Augmented Generation (RAG) templates in English.
"""

from string import Template

SYSTEM_PROMPT = Template(
    "\n".join(
        [
            "You are a helpful assistant that helps people find information.",
            (
                "You are given the following extracted parts of a long document and a query. "
                "Provide a conversational answer based on the context provided. "
                "Ignore the documents that are not relevant to the user's query. "
                "You have to generate response in the same language as the user's query."
            ),
            (
                "If you don't know the answer, just apologize and say that you don't know. "
                "Don't try to make up an answer."
                "Be precise and concise in your response. Avoid unnecessary information."
                "Use three sentences maximum."
            ),
            (
                "You **must** cite the context document index for each piece of "
                "information you use in your answer "
                "in this strict format *[doc index]* (e.g., *[1]*) whenever applicable."
            ),
            (
                "Use structured output whenever applicable "
                "to make your answer clear and easy to read. "
                "(e.g., bullet points, numbered lists, tables, new lines, etc.)"
            ),
            "",
        ]
    )
)

CONTEXT_ENTRY = Template(
    "\n".join(
        [
            "## Context Document: $index",
            "### Content: $content",
            "",
        ]
    )
)

FOOTER = Template(
    "\n".join(
        [
            "Based only on the above documents, please generate an answer for the user.",
            "## Query:",
            "$query",
            "",
            "## Answer:",
        ]
    )
)
