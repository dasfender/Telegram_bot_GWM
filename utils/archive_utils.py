import os
import zipfile
from datetime import datetime

def create_request_archive(dealer_code: str):
    base_folder = os.path.join("requests", dealer_code)
    if not os.path.exists(base_folder):
        return None

    request_dates = sorted(os.listdir(base_folder), reverse=True)
    if not request_dates:
        return None

    last_request_folder = os.path.join(base_folder, request_dates[0])
    archive_name = f"{dealer_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    archive_path = os.path.join("requests", archive_name)

    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(last_request_folder):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, base_folder)
                zipf.write(full_path, arcname)

    return archive_path
