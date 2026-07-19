import os


def save_markdown(filename, content):

    os.makedirs("reports", exist_ok=True)

    filepath = os.path.join("reports", filename)

    with open(filepath, "w", encoding="utf-8") as file:
        file.write(content)

    return filepath