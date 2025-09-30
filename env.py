import os

DEBUG = os.getenv("DEBUG", "").lower() in ["true", "1", "t"]
NTHREADS = int(os.getenv("NTHREADS", str(os.cpu_count())))
VERSION = "0.0.1"
