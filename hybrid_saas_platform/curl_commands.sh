#!/bin/bash
# Kloud Cloud API - cURL Commands
# Generated: 2026-01-11T07:43:20.853661

# Set your token first:
# export TOKEN='your-auth-token'

# /health - GET
# Kontrollon gjendjen e shëndetit të sistemit. Kthen statusin e përgjithshëm të pl...
curl -X GET "https://api.kloud.com/health" -H "Authorization: Bearer $TOKEN"

# /status - GET
# Merr statusin e detajuar të sistemit duke përfshirë metrikat e CPU, RAM, disk dh...
curl -X GET "https://api.kloud.com/status" -H "Authorization: Bearer $TOKEN"

# /api/system-status - GET
# Kthen statusin e plotë të sistemit industrial duke përfshirë të gjitha shërbimet...
curl -X GET "https://api.kloud.com/api/system-status" -H "Authorization: Bearer $TOKEN"

# /db/ping - GET
# Teston lidhjen me bazën e të dhënave PostgreSQL. Kthen kohën e përgjigjes dhe st...
curl -X GET "https://api.kloud.com/db/ping" -H "Authorization: Bearer $TOKEN"

# /redis/ping - GET
# Teston lidhjen me Redis cache. Kthen statusin, memorien e përdorur dhe numrin e ...
curl -X GET "https://api.kloud.com/redis/ping" -H "Authorization: Bearer $TOKEN"

# /api/ask - POST
# Endpoint i inteligjencës artificiale për pyetje-përgjigje. Pranon pyetje në gjuh...
curl -X POST "https://api.kloud.com/api/ask" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question": "Çfarë është Kloud?", "context": "Platformë neuro-audio", "include_details": true}' 

# /neural-symphony - GET
# Gjeneron muzikë brain-sync në kohë reale bazuar në parametrat e specifikuar. Kth...
curl -X GET "https://api.kloud.com/neural-symphony" -H "Authorization: Bearer $TOKEN" -H "Accept: audio/wav" --output symphony.wav

# /api/uploads/eeg/process - POST
# Ngarkon dhe përpunon skedarë EEG (formatet .edf, .bdf, .fif). Ekstrakon kanalet,...
curl -X POST "https://api.kloud.com/api/uploads/eeg/process" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@brain_scan.edf"

# /api/uploads/audio/process - POST
# Ngarkon dhe përpunon skedarë audio për analizë. Ekstrakon karakteristika audio, ...
curl -X POST "https://api.kloud.com/api/uploads/audio/process" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@recording.wav"

# /billing/paypal/order - POST
# Krijon një porosi PayPal për pagesë. Kthen ID-në e porosisë dhe URL-në për aprov...
curl -X POST "https://api.kloud.com/billing/paypal/order" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"intent": "CAPTURE", "purchase_units": [{"amount": {"currency_code": "EUR", "value": "10.00"}}]}'  

# /billing/stripe/payment-intent - POST
# Krijon një Stripe Payment Intent për pagesë me kartë ose SEPA. Kthen client_secr...
curl -X POST "https://api.kloud.com/billing/stripe/payment-intent" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"amount": 1000, "currency": "eur", "payment_method_types": ["sepa_debit"]}'  

# /asi/status - GET
# Merr statusin e ASI Trinity (ALBA, ALBI, JONA). Kthen gjendjen e secilit agjent ...
curl -X GET "https://api.kloud.com/asi/status" -H "Authorization: Bearer $TOKEN"

# /asi/health - GET
# Kontrollon shëndetin e ASI Trinity. Kthen health check të detajuar për secilin k...
curl -X GET "https://api.kloud.com/asi/health" -H "Authorization: Bearer $TOKEN"

# /asi/execute - POST
# Ekzekuton një komandë në ASI Trinity. Mund të dërgojë komanda tek ALBA, ALBI ose...
curl -X POST "https://api.kloud.com/asi/execute" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command": "status", "agent": "trinity", "parameters": {}}'  

# /api/alba/health - GET
# Kontrollon shëndetin e ALBA Network Manager. Kthen metrikat e rrjetit, latency d...
curl -X GET "https://api.kloud.com/api/alba/health" -H "Authorization: Bearer $TOKEN"

# /asi/alba/metrics - GET
# Merr metrikat real-time të ALBA nga Prometheus. Përfshin CPU, Memory, Network La...
curl -X GET "https://api.kloud.com/asi/alba/metrics" -H "Authorization: Bearer $TOKEN"

# /asi/albi/metrics - GET
# Merr metrikat real-time të ALBI Neural nga Prometheus. Përfshin Goroutines, Neur...
curl -X GET "https://api.kloud.com/asi/albi/metrics" -H "Authorization: Bearer $TOKEN"

# /asi/jona/metrics - GET
# Merr metrikat real-time të JONA Coordinator nga Prometheus. Përfshin HTTP Reques...
curl -X GET "https://api.kloud.com/asi/jona/metrics" -H "Authorization: Bearer $TOKEN"

# /brain/youtube/insight - GET
# Analizon një video YouTube dhe kthen insights, transkript dhe analiza sentimente...
curl -X GET "https://api.kloud.com/brain/youtube/insight?video_id=dQw4w9WgXcQ" -H "Authorization: Bearer $TOKEN"

# /brain/music/brainsync - POST
# Gjeneron muzikë brain-sync bazuar në skedarin EEG dhe modalitetin e kërkuar (rel...
curl -X POST "https://api.kloud.com/brain/music/brainsync?mode=relax" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@eeg_data.edf"


