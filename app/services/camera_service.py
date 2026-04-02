import subprocess
from datetime import datetime
from pathlib import Path


class CameraService:
    def __init__(self, output_dir="."):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def take_picture(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.output_dir / f"capture_{timestamp}.jpg"

        try:
            subprocess.run(
                [
                    "rpicam-still",
                    "-o",
                    str(filename),
                    "-t",
                    "1000",
                    "--nopreview",
                ],
                check=True,
            )
            print(f"📸 Captured image: {filename}")
            return str(filename)

        except Exception as e:
            print(f"Camera error: {e}")
            return None
