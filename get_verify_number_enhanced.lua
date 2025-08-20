-- Enhanced get_verify_number.lua with detailed metrics collection
wrk.method = "GET"
wrk.headers["Cookie"] = "_ga_89597DLSJP=GS2.1.s1755283508$o6$g1$t1755288480$j60$l0$h0; _ga=GA1.1.1088252796.1755035926"
wrk.headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64; rv:143.0) Gecko/20100101 Firefox/143.0"
wrk.headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
wrk.headers["Accept-Language"] = "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3"
wrk.headers["Accept-Encoding"] = "gzip, deflate, br"
wrk.headers["Upgrade-Insecure-Requests"] = "1"
wrk.headers["Sec-Fetch-Dest"] = "document"
wrk.headers["Sec-Fetch-Mode"] = "navigate"
wrk.headers["Sec-Fetch-Site"] = "none"
wrk.headers["Sec-Fetch-User"] = "?1"
wrk.headers["Priority"] = "u=0, i"
wrk.headers["Te"] = "trailers"

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
    print("=== GET VERIFY NUMBER RESULTS ===")
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
    print("=== END GET VERIFY NUMBER ===")
end
