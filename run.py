import os

import uvicorn

reload = True if os.environ.get("ENVIRONMENT") == "local" else False
workers = os.environ.get("CPU", "1")

if __name__ == "__main__":
    port: int = int(os.environ.get("PORT", 8080))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=reload,
        workers=int(workers)
    )