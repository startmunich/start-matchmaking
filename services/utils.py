import asyncio
import requests
import os

async def download(_url: str, _temp_dir: str, _auth_header: dict[str, str]) -> str:
    print("utils | download_temp")
    pdf_filename = _url.split('/')[-1]
    pdf_path = os.path.join(_temp_dir, pdf_filename)
    response = requests.get(_url, headers=_auth_header)
    print(f"utils | download_temp | {response.status_code}")

    with open(pdf_path, 'wb') as f:
        f.write(response.content)

    print(f"utils | download_temp | {pdf_path}")
    return pdf_path
