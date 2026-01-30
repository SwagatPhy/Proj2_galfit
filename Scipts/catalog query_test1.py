import pandas as pd
import urllib.request
import os
import gzip
import shutil

# Load your CSV
df = pd.read_csv('galaxy_parameters_dr7.csv')

# Create output directory
os.makedirs('sdss_images', exist_ok=True)

# Get unique fields
unique_fields = df[['run', 'rerun', 'camcol', 'field']].drop_duplicates()

print(f"Downloading {len(unique_fields)} fields for {len(df)} galaxies\n")

# Download each field
for idx, row in unique_fields.iterrows():
    run = int(row['run'])
    rerun = int(row['rerun'])
    camcol = int(row['camcol'])
    field = int(row['field'])
    
    print(f"\nField {field} (run={run}, camcol={camcol})")
    print("-" * 60)
    
    # CORRECTED filename format for DR7
    filename = f"fpC-{run:06d}-r{camcol}-{field:04d}.fits"
    filename_gz = f"fpC-{run:06d}-r{camcol}-{field:04d}.fit.gz"
    
    output_path = os.path.join('sdss_images', filename)
    
    if os.path.exists(output_path):
        print(f"✓ Already exists: {filename}")
        continue
    
    # Try multiple URL patterns (SDSS paths vary)
    urls = [
        # Pattern 1: Standard DR7 structure
        f"https://data.sdss.org/sas/dr7/boss/photoObj/frames/{rerun}/{run}/{camcol}/{filename_gz}",
        # Pattern 2: Alternative path
        f"http://das.sdss.org/imaging/{run}/{rerun}/corr/{camcol}/{filename_gz}",
        # Pattern 3: Legacy path
        f"https://dr7.sdss.org/sas/dr7/boss/photoObj/frames/{rerun}/{run}/{camcol}/{filename_gz}",
        # Pattern 4: Direct DAS
        f"http://data.sdss3.org/sas/dr7/boss/photoObj/frames/{rerun}/{run}/{camcol}/{filename_gz}",
    ]
    
    temp_path = os.path.join('sdss_images', filename_gz)
    success = False
    
    for url_idx, url in enumerate(urls, 1):
        try:
            print(f"Attempt {url_idx}: {url}")
            urllib.request.urlretrieve(url, temp_path)
            
            print(f"✓ Downloaded! Decompressing...")
            with gzip.open(temp_path, 'rb') as f_in:
                with open(output_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            os.remove(temp_path)
            
            size_mb = os.path.getsize(output_path) / (1024*1024)
            print(f"✓✓ SUCCESS! {filename} ({size_mb:.1f} MB)")
            success = True
            break
            
        except Exception as e:
            print(f"✗ Failed: {e}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            continue
    
    if not success:
        print(f"✗✗ All download attempts failed for field {field}")

print("\n" + "="*60)
print("Download complete! Check 'sdss_images' directory")
print("="*60)