# download_dataset.py
import requests
import os
from tqdm import tqdm

# Stable raw GitHub CDN link for the exact same Online Retail dataset
url = "https://github.com/dipanjanS/practical-machine-learning-with-python/raw/master/notebooks/Ch08_Customer_Segmentation_and_Effective_Cross_Selling/Online%20Retail.xlsx"
dest = os.path.join("data", "raw", "Online Retail.xlsx")

# Ensure raw folder exists
os.makedirs(os.path.dirname(dest), exist_ok=True)

print(f"⬇️ Fetching stable 'Online Retail.xlsx' from GitHub CDN...")
print(f"Destination: {os.path.abspath(dest)}")

try:
    # Use requests to download the file with a stream
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

    total_size_in_bytes = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 Kibibyte

    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True, desc="Downloading")

    with open(dest, 'wb') as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)

    progress_bar.close()

    if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
        print("❌ ERROR, file size mismatch.")
    else:
        print(f"\n✅ Download complete!")
        final_size_mb = os.path.getsize(dest) / (1024 * 1024)
        print(f"📊 Verified Local File Size: {final_size_mb:.2f} MB")

except requests.exceptions.RequestException as e:
    print(f"❌ Download failed: {e}")

