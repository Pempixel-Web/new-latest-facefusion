import os
import uuid
import subprocess
import requests


TMP_DIR = "/tmp"


def download_file(url, output_path):
    r = requests.get(url, stream=True)
    r.raise_for_status()

    with open(output_path, "wb") as f:
        for chunk in r.iter_content(8192):
            if chunk:
                f.write(chunk)


def handler(job):
    job_input = job["input"]

    source_url = job_input["source"]
    target_url = job_input["target"]

    job_id = str(uuid.uuid4())

    source_path = os.path.join(TMP_DIR, f"{job_id}_source.jpg")
    target_path = os.path.join(TMP_DIR, f"{job_id}_target.jpg")
    output_path = os.path.join(TMP_DIR, f"{job_id}_output.jpg")

    download_file(source_url, source_path)
    download_file(target_url, target_path)

    command = [
        "python",
        "facefusion.py",
        "headless-run",
        "--source-paths",
        source_path,
        "--target-path",
        target_path,
        "--output-path",
        output_path
    ]

    subprocess.run(command, check=True)

    return {
        "success": True,
        "output_path": output_path
    }