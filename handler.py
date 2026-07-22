import os
import uuid
import base64
import subprocess
import requests

TMP_DIR = "/tmp"


def download_file(url, output_path):
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(output_path, "wb") as f:
        for chunk in response.iter_content(8192):
            if chunk:
                f.write(chunk)


def image_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def handler(job):
    try:
        job_input = job.get("input", {})

        source_url = job_input.get("source")
        target_url = job_input.get("target")

        if not source_url:
            return {
                "success": False,
                "error": "Missing 'source' image URL."
            }

        if not target_url:
            return {
                "success": False,
                "error": "Missing 'target' image URL."
            }

        uid = str(uuid.uuid4())

        source_path = os.path.join(TMP_DIR, f"{uid}_source.jpg")
        target_path = os.path.join(TMP_DIR, f"{uid}_target.jpg")
        output_path = os.path.join(TMP_DIR, f"{uid}_output.jpg")

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

        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return {
                "success": False,
                "error": result.stderr,
                "stdout": result.stdout
            }

        if not os.path.exists(output_path):
            return {
                "success": False,
                "error": "FaceFusion finished but no output image was created."
            }

        return {
            "success": True,
            "image": image_to_base64(output_path)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }