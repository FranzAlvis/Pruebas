-- Enhanced post_pagos.lua with detailed metrics collection
wrk.method = "POST"
wrk.path   = "/api/pagos/ProcessMessage"
wrk.body   = '{"Header":"pP4FGrZEnrKaia6kSgXcva34C44GnftYMvAPP66nnzOMIlr7muTFWYTXSP5AmfiRPZO08cCGO5U5tzTmA4sheqK7DZwPCdhKz4VyrqbghmGUSy5bRrrMECB9HRuAQkgKWwqQkcwFvQigrbTNF4e+NGFjLW2aigJ+88i2ydtzqunPHGCEPyQVg8V6Wti4RQ2ptdN64uqf8wxZcZ4LKYAKgdNCN/w50pVGWOyia2i3Hc/KvposQ5FenkEsHcLsEwEG","InputData":"wGN3pmdjlx/4+0hXDisYnGsSR5rO7/wvko5LEA1EvlRoRrmYMc7G4PBPl+w0CTHQ9QnB5YL0aC18FKyRwHMHpA=="}'

wrk.headers = {
  ["Host"] = "ws.pagosbolivia.com.bo:8443",
  ["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64; rv:143.0) Gecko/20100101 Firefox/143.0",
  ["Accept"] = "application/json, text/plain, */*",
  ["Accept-Language"] = "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
  ["Accept-Encoding"] = "gzip, deflate, br",
  ["Authorization"] = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiYXNlV2ViQXBpU3ViamVjdCIsImp0aSI6IjY1ZGVkY2U2LWY0OTQtNGVkNy05MzI4LTg0ZGRhM2FkOGJiNCIsImlhdCI6IjIxLzgvMjAyNSAwMjo0NDo0NyIsImVtcHJlc2EiOiJQQUdPQk9MIiwidXN1YXJpbyI6IjlRRXFYWGM2Wmt0R0Y1WGZrd0hnM0E9PSIsInBhc3N3b3JkIjoiR2lzR0NCejFkTzl4aDBxQ0ZtdWQ1VUdXSVozQ1ZhMkI5akRLd09BK1VocFRDc2pVLzFRVkFEWmlDNVJvUDVFWiIsImV4cCI6MTc1NTc0Nzg4NywiaXNzIjoiaHR0cDovL2xvY2FsaG9zdC8iLCJhdWQiOiJodHRwOi8vbG9jYWxob3N0LyJ9.gFF7TBBOVvijonS54LEW9OGJaUUDE50B2SG6PCkXUrc",
  ["Content-Type"] = "application/json",
  ["Origin"] = "https://pagosbolivia.com.bo",
  ["Referer"] = "https://pagosbolivia.com.bo/",
  ["Sec-Fetch-Dest"] = "empty",
  ["Sec-Fetch-Mode"] = "cors",
  ["Sec-Fetch-Site"] = "same-site",
  ["Priority"] = "u=0",
  ["Te"] = "trailers"
}


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
