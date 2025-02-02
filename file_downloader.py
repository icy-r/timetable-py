import sys
import urllib.request
import re
import time

def human_readable(size, decimal_places=2):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.{decimal_places}f} {unit}"
        size /= 1024
    return f"{size:.{decimal_places}f} PB"

def download_file(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        u = urllib.request.urlopen(req)
        meta = u.info()
        
        # Extract file name from Content-Disposition header
        content_disposition = meta.get("Content-Disposition")
        if content_disposition:
            file_name = re.findall('filename="(.+)"', content_disposition)
            if file_name:
                file_name = file_name[0]
            else:
                file_name = 'file.mkv'
        else:
            file_name = 'file.mkv'
        
        f = open(file_name, 'wb')
        file_size = int(meta.get("Content-Length"))
        print(f"Downloading: {file_name} Size: {human_readable(file_size)}")
        
        file_size_dl = 0
        block_sz = 8192
        start_time = time.time()
        
        try:
            while True:
                buffer = u.read(block_sz)
                if not buffer:
                    break
                
                file_size_dl += len(buffer)
                f.write(buffer)
                
                elapsed_time = time.time() - start_time
                speed = file_size_dl / elapsed_time if elapsed_time > 0 else 0
                percent = (file_size_dl * 100.) / file_size
                
                status = (f"Downloaded: {human_readable(file_size_dl)} of {human_readable(file_size)} "
                          f"({percent:3.2f}%)  Speed: {human_readable(speed)}/s")
                print(status, end='\r')
        except KeyboardInterrupt:
            print("\nDownload cancelled by user.")
            f.close()
            return
        
        f.close()
        print("\nDownload completed successfully.")
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    while True:
        url = input("Enter download URL (or type 'exit' to quit): ").strip()
        if url.lower() == 'exit':
            break
        if url:
            download_file(url)
        else:
            print("Please enter a valid URL.")