import base64
import os
from pathlib import Path

import tqdm
from openai import OpenAI

import pandas as pd
import typer


def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')


def main(
    screenshots_folder: Path = typer.Option(...),
    output_csv_path: Path = typer.Option(...)
) -> None:
    """Create chunks from monographs."""
    all_images = list(screenshots_folder.glob("*.png"))[:100]

    output_csv_path.parent.mkdir(parents=True, exist_ok=True)
    all_dicts = []

    client = OpenAI()

    for image_path in tqdm.tqdm(all_images):
        base64_image = encode_image(image_path)
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Describe the image below quickly (one or two sentence) so that we can group it to very similar ones"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens= 50
        )

        all_dicts.append({"image_name":image_path.name, "description": response.choices[0].message.content})
    pd.DataFrame(all_dicts).to_csv(output_csv_path)

if __name__ == "__main__":
    typer.run(main)
