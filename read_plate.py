import os
from ollama import chat
from ollama import ChatResponse


def read_plate(image_path: str, model: str) -> str | None:
    ollama_response = _ollama_read_image(image_path, model)
    if ollama_response is None: return None

    plate = ollama_response.message.content
    return plate


def _ollama_read_image(image_path: str, model: str) -> ChatResponse | None:
    if not os.path.isfile(image_path) or not os.path.exists(image_path):
        return None

    prompt: str = ("Extract the car plate number from the image and return it as a string without any spaces. "
                   "If no plate is present, respond with 'No plate found'.")
    response = chat(
        model=model,
        messages=[{
            'role': 'user',
            'content': prompt,
            'images': [image_path],
        }],
        options={'temperature': 0},
    )

    content = response.message.content
    if "No plate found" in content:
        return None

    return response
