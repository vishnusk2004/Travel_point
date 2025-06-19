import threading
import subprocess
import sys
import os

SCRAPER1 = os.path.join(os.path.dirname(__file__), 'scraper_codes', 'onemile.py')
SCRAPER2 = os.path.join(os.path.dirname(__file__), 'scraper_codes', 'upgraded_points.py')


def run_script(script_path):
    subprocess.run([sys.executable, script_path])

if __name__ == "__main__":
    t1 = threading.Thread(target=run_script, args=(SCRAPER1,))
    t2 = threading.Thread(target=run_script, args=(SCRAPER2,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print("Both scrapers finished.") 