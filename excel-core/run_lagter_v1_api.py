from __future__ import annotations

import os

import uvicorn

from lagter_v1_api import app


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "4010"))
    uvicorn.run(app, host="0.0.0.0", port=port)
