import subprocess

import time

if __name__ == "__main__":
    while True:
        print("Starting...")
        process = subprocess.Popen("python xhamster_spider_agency.py")
        print("Started, sleeping.")
        time.sleep(60 * 15)
        process.kill()
        time.sleep(5)
