# -*- coding: utf-8 -*-
"""
🔌 BINARY API MIDDLEWARE
========================
Middleware që konverton responses në binary format REAL!

Formats:
- application/json (default)
- application/cbor (CBOR2)
- application/msgpack (MessagePack)
- application/octet-stream (Custom Binary CLSN)
- application/x-kloud (Custom Binary CLSN)

Author: Kloud Team
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Any, Dict, Optional
import json

from .binary_protocols import get_binary_service, BinaryFormat, BinaryEncoder


class BinaryResponseMiddleware(BaseHTTPMiddleware):
    """Middleware për binary responses"""
    
    BINARY_CONTENT_TYPES = {
        "application/cbor": BinaryFormat.CBOR2,
        "application/cbor2": BinaryFormat.CBOR2,
        "application/msgpack": BinaryFormat.MSGPACK,
        "application/x-msgpack": BinaryFormat.MSGPACK,
        "application/octet-stream": BinaryFormat.CUSTOM_BINARY,
        "application/x-kloud": BinaryFormat.CUSTOM_BINARY,
        "application/x-clsn": BinaryFormat.CUSTOM_BINARY,
    }
    
    async def dispatch(self, request: Request, call_next):
        # Check Accept header
        accept = request.headers.get("Accept", "application/json")
        
        # Check query param override
        format_param = request.query_params.get("_format", "")
        if format_param:
            format_map = {
                "cbor": "application/cbor",
                "msgpack": "application/msgpack",
                "binary": "application/octet-stream",
                "clsn": "application/x-kloud",
                "json": "application/json"
            }
            accept = format_map.get(format_param.lower(), accept)
        
        # Get response
        response = await call_next(request)
        
        # Check if we should convert to binary
        if accept in self.BINARY_CONTENT_TYPES:
            binary_format = self.BINARY_CONTENT_TYPES[accept]
            
            # Read response body
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            
            try:
                # Parse JSON response
                data = json.loads(body.decode('utf-8'))
                
                # Encode to binary
                encoder = BinaryEncoder(binary_format)
                binary_data = encoder.encode(data, binary_format)
                
                return Response(
                    content=binary_data,
                    media_type=accept,
                    headers={
                        "X-Binary-Format": binary_format.name,
                        "X-Original-Size": str(len(body)),
                        "X-Binary-Size": str(len(binary_data)),
                        "X-Compression-Ratio": f"{len(body)/len(binary_data):.2f}" if len(binary_data) > 0 else "0"
                    }
                )
            except Exception as e:
                # Return original if conversion fails
                return Response(
                    content=body,
                    media_type="application/json",
                    headers={"X-Binary-Error": str(e)}
                )
        
        return response


class BinaryResponse(Response):
    """Custom binary response class"""
    
    def __init__(
        self,
        content: Any,
        format: BinaryFormat = BinaryFormat.CUSTOM_BINARY,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None
    ):
        encoder = BinaryEncoder(format)
        binary_data = encoder.encode(content, format)
        
        # BINARY ONLY - no JSON
        media_type_map = {
            BinaryFormat.CBOR2: "application/cbor",
            BinaryFormat.MSGPACK: "application/msgpack",
            BinaryFormat.CUSTOM_BINARY: "application/x-kloud",
            BinaryFormat.COMPRESSED_CBOR: "application/gzip",
        }
        
        media_type = media_type_map.get(format, "application/octet-stream")
        
        response_headers = headers or {}
        response_headers.update({
            "X-Binary-Format": format.name,
            "X-Binary-Size": str(len(binary_data)),
        })
        
        super().__init__(
            content=binary_data,
            status_code=status_code,
            headers=response_headers,
            media_type=media_type
        )


def create_binary_response(data: Any, format: str = "clsn") -> Response:
    """Helper function për binary responses"""
    # BINARY ONLY - CBOR2/MSGPACK/CUSTOM
    format_map = {
        "cbor": BinaryFormat.CBOR2,
        "cbor2": BinaryFormat.CBOR2,
        "msgpack": BinaryFormat.MSGPACK,
        "binary": BinaryFormat.CUSTOM_BINARY,
        "clsn": BinaryFormat.CUSTOM_BINARY,
        "compressed": BinaryFormat.COMPRESSED_CBOR,
    }
    
    binary_format = format_map.get(format.lower(), BinaryFormat.CUSTOM_BINARY)
    return BinaryResponse(content=data, format=binary_format)

