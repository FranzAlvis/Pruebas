-- Enhanced post_pagos.lua with detailed metrics collection
wrk.method = "POST"
wrk.body   = '{"Header":"pP4FGrZEnrKaia6kSgXcvdscM9Ua3VkvH1ZZhh+LV0uGaaMhYhBygg3BtNGDBOlsRxfxNkEiaOyovr9iEaDYzZZBbTc9Y8uNsbjbIFYJTdo3c4G0jJi7GgtGsRLuYCAM/y+vjR7OeiuvWQGoQa0SDhkwm1az88pe87r5iME1YGoTTNBQIrc1nssKtIBnptIKPgKPS03AreXSdIlF0lgSjnizu9kYg4Fa+cfnDBzERybnjRwASFTZiYmbxAU5uxKk","InputData":"eoU/tLdp/uZZ6oAwyd8Hip+51JDbYA2mmozfd6xgZd+rpFpHO3pSuDuJ89tMPgcSnZsSSyiy82/e7pObseyKRqNZD/Z/A5Pzrgdx06OXuZ85qcxquXSmpDGjKT2E2JcUXpT/tbeWyPwg1sGIBsD2jIEJYbrDe+yVBhQFrT/l0epYf4DiEoe/9B3EsHLFYI4Vdw3jv5/OIElsqUlK7vhAhHkXIKL1KKg7F4/9FlY7md2Bf/lPIuiOVWl9n5JlA4m/6TVlL4FbfQG2/8MjLBEZig=="}'
wrk.headers["Content-Type"] = "application/json"
wrk.headers["Authorization"] = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiYXNlV2ViQXBpU3ViamVjdCIsImp0aSI6IjAzOTZjZjdjLTNiMzYtNGY1Zi05ODM1LTViY2YwZTIzMjNhMiIsImlhdCI6IjIwLzgvMjAyNSAyMDozMTowMiIsImVtcHJlc2EiOiJQQUdPQk9MIiwidXN1YXJpbyI6IjlRRXFYWGM2Wmt0R0Y1WGZrd0hnM0E9PSIsInBhc3N3b3JkIjoiR2lzR0NCejFkTzl4aDBxQ0ZtdWQ1VUdXSVozQ1ZhMkI5akRLd09BK1VocFRDc2pVLzFRVkFEWmlDNVJvUDVFWiIsImV4cCI6MTc1NTcyNTQ2MiwiaXNzIjoiaHR0cDovL2xvY2FsaG9zdC8iLCJhdWQiOiJodHRwOi8vbG9jYWxob3N0LyJ9.2klu-EksD9f0OlZQ7clVwQK3Oaa7eoy5Ggu07Jywmh0"

-- Metrics collection
local responses = {}
local status_codes = {}
local errors = {}

function init(args)
    responses = {}
    status_codes = {}
    errors = {}
end

function response(status, headers, body)
    if status_codes[status] == nil then
        status_codes[status] = 0
    end
    status_codes[status] = status_codes[status] + 1
    
    table.insert(responses, {
        status = status,
        size = string.len(body),
        timestamp = os.time()
    })
end

function done(summary, latency, requests)
    print("=== POST PAGOS RESULTS ===")
    print(string.format("Requests: %d", summary.requests))
    print(string.format("Duration: %.2fs", summary.duration / 1000000))
    print(string.format("Bytes: %d", summary.bytes))
    print(string.format("Errors: %d", summary.errors.connect + summary.errors.read + summary.errors.write + summary.errors.status + summary.errors.timeout))
    print(string.format("RPS: %.2f", summary.requests / (summary.duration / 1000000)))
    
    print("\nStatus Code Distribution:")
    for status, count in pairs(status_codes) do
        print(string.format("  %d: %d requests", status, count))
    end
    
    print(string.format("\nLatency Stats (ms):"))
    print(string.format("  Min: %.2f", latency.min / 1000))
    print(string.format("  Max: %.2f", latency.max / 1000))
    print(string.format("  Mean: %.2f", latency.mean / 1000))
    print(string.format("  50th: %.2f", latency:percentile(50) / 1000))
    print(string.format("  90th: %.2f", latency:percentile(90) / 1000))
    print(string.format("  95th: %.2f", latency:percentile(95) / 1000))
    print(string.format("  99th: %.2f", latency:percentile(99) / 1000))
    print("=== END POST PAGOS ===")
end
