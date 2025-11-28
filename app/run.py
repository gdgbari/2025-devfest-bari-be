import os

import uvicorn

reload = os.environ.get("DEBUG").lower() in ["1", "true"]
workers = os.environ.get("CPU", str(os.cpu_count()))

if __name__ == "__main__":
    port: int = int(os.environ.get("PORT", 8080))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=reload,
        workers=int(workers)
    )