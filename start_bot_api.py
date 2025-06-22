#!/usr/bin/env python3
"""Start the ChipEngine Bot API server."""

import uvicorn
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    uvicorn.run(
        "chipengine.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )