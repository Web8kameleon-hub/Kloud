#!/usr/bin/env python3
"""Generate Postman Collection from OpenAPI specification"""

import json
import yaml
import uuid

def generate_postman_collection():
    # Lexo OpenAPI JSON
    with open('openapi.json', 'r', encoding='utf-8') as f:
        openapi_spec = json.load(f)
    
    # Info
    info = openapi_spec.get('info', {})
    
    # Konfiguro Postman Collection
    postman_collection = {
        "info": {
            "_postman_id": str(uuid.uuid4()),
            "name": f"{info.get('title', 'API')} - Postman Collection",
            "description": info.get('description', ''),
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": [],
        "variable": [
            {
                "key": "baseUrl",
                "value": "http://localhost:8000",
                "type": "string"
            },
            {
                "key": "token",
                "value": "your-jwt-token-here",
                "type": "string"
            }
        ],
        "auth": {
            "type": "bearer",
            "bearer": [
                {
                    "key": "token",
                    "value": "{{token}}",
                    "type": "string"
                }
            ]
        }
    }
    
    # Paths
    paths = openapi_spec.get('paths', {})
    folders = {}
    
    for path, methods in paths.items():
        for method, details in methods.items():
            if method.lower() not in ['get', 'post', 'put', 'patch', 'delete', 'options', 'head']:
                continue
            
            # Get folder from tags
            tags = details.get('tags', ['General'])
            folder_name = tags[0] if tags else 'General'
            
            if folder_name not in folders:
                folders[folder_name] = {
                    "_postman_id": str(uuid.uuid4()),
                    "name": folder_name,
                    "item": []
                }
            
            # Build request
            request = {
                "method": method.upper(),
                "url": {
                    "raw": "{{baseUrl}}" + path,
                    "host": ["{{baseUrl}}"],
                    "path": path.strip('/').split('/')
                }
            }
            
            # Headers
            headers = [
                {
                    "key": "Content-Type",
                    "value": "application/json",
                    "type": "text"
                },
                {
                    "key": "Authorization",
                    "value": "Bearer {{token}}",
                    "type": "text"
                }
            ]
            request["header"] = headers
            
            # Body
            if method.lower() in ['post', 'put', 'patch']:
                body_schema = details.get('requestBody', {}).get('content', {}).get('application/json', {}).get('schema', {})
                request["body"] = {
                    "mode": "raw",
                    "raw": json.dumps(body_schema, indent=2),
                    "options": {"raw": {"language": "json"}}
                }
            
            # Request item
            item = {
                "_postman_id": str(uuid.uuid4()),
                "name": details.get('summary', path),
                "request": request,
                "response": []
            }
            
            folders[folder_name]["item"].append(item)
    
    # Add folders to collection
    postman_collection["item"] = list(folders.values())
    
    # Write collection
    with open('kloud-cloud.postman_collection.json', 'w', encoding='utf-8') as f:
        json.dump(postman_collection, f, indent=2, ensure_ascii=False)
    
    # Count endpoints
    endpoint_count = sum(len(folder['item']) for folder in folders.values())
    
    print(f'✓ Postman Collection generated')
    print(f'  - {len(folders)} categories')
    print(f'  - {endpoint_count} endpoints')
    print(f'  - Size: {len(json.dumps(postman_collection).encode())/1024:.1f} KB')

if __name__ == '__main__':
    generate_postman_collection()


