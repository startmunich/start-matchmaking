import asyncio
import requests
import os
import tempfile

async def download_temp(_url: str, _auth_header: dict[str, str]) -> str:
    with tempfile.TemporaryDirectory() as temp_dir:
        pdf_filename = _url.split('/')[-1]
        pdf_path = os.path.join(temp_dir, pdf_filename)
        response = asyncio.run(requests.get(_url, headers=_auth_header))

        with open(pdf_path, 'wb') as f:
            f.write(response.content)
        return pdf_path
