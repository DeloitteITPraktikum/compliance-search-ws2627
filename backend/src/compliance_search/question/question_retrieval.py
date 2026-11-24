from compliance_search.models import AskRequest


def retrieve_question() -> tuple[str, AskRequest]:
    """
    Fragt Sprache und Benutzerfrage ab.
    
    Returns:
        tuple[str, AskRequest]: (language, request)
    """

    # Sprache auswählen
    language = input("Select language [DE/EN]: ").strip().upper()

    while language not in ["DE", "EN"]:
        language = input("Invalid input. Select language [DE/EN]: ").strip().upper()

    # Frage stellen
    if language == "DE":
        question = input("Bitte stellen Sie Ihre Frage: ")
    else:
        question = input("Please enter your question: ")

    # Fragezeichen am Ende entfernen
    question = question.rstrip("?").strip()

    return language, AskRequest(question=question)


if __name__ == "__main__":
    language, request = retrieve_question()

    print("\n--- Result ---")
    print(f"Language: {language}")
    print(f"Question: {request.question}")
