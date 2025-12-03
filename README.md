# AgentFleet Demo: Add Rate Limiting to URL Shortener

This demo showcases a **realistic AgentFleet use case**: adding a new feature (rate limiting) to an existing application.

## The Application

`app.py` is a simple URL shortener API built with Flask:
- **POST /shorten** - Create shortened URLs
- **GET /<short_code>** - Redirect to original URL
- **GET /stats/<short_code>** - View click statistics

**The Problem:** No rate limiting! The API can be abused with unlimited requests.

## The Task

Add rate limiting to protect the API endpoints:
- `/shorten` endpoint: 10 requests per minute per user
- `/<short_code>` redirect: 100 requests per minute per user

## Approaches Being Compared

Three different rate limiting strategies will be implemented:

### 1. Token Bucket
Accumulates tokens at a fixed rate. Each request consumes one token.

**Pros:** Smooth rate limiting, allows controlled bursts
**Cons:** More complex state management

### 2. Sliding Window
Tracks exact timestamps of requests in a rolling window.

**Pros:** Most accurate, handles boundary cases correctly
**Cons:** Higher memory usage for high-traffic scenarios

### 3. Fixed Window
Divides time into fixed intervals, resets counters at boundaries.

**Pros:** Very simple, memory efficient
**Cons:** Boundary bug—allows 2x requests at window edges!

## Running the Live Demo

### Step 1: Install dependencies
```bash
pip install flask
```

### Step 2: See the current app (no rate limiting)
```bash
python app.py
# Server runs on http://localhost:5000
# Try: curl -X POST http://localhost:5000/shorten -H "Content-Type: application/json" -d '{"url": "https://example.com"}'
```

### Step 3: Run AgentFleet tournament
```bash
cd ..
agentfleet "Add rate limiting to app.py: 10 req/min on /shorten, 100 req/min on redirects, per-user. Use the {approach} approach." \
           "Token bucket" "Sliding window" "Fixed window" \
           --work-dir agentfleet-demo-ratelimiter/work
```

### Step 4: Review results
AgentFleet will:
1. Generate evaluation criteria (tests for rate limiting)
2. Run 3 agents in parallel, each modifying app.py differently
3. Test each implementation
4. Rank by correctness, simplicity, performance

**Expected winner:** Sliding window (most accurate, handles boundaries)
**Expected failure:** Fixed window (boundary bug caught by tests)

## Reference Implementations

The `reference/` directory shows what each approach looks like when fully integrated:
- `app_with_token_bucket.py` - Token bucket approach
- `app_with_sliding_window.py` - Sliding window approach
- `app_with_fixed_window.py` - Fixed window approach (with boundary bug)

**Important:** AgentFleet agents don't see these! They start with the unmodified `app.py` and add rate limiting from scratch.

## Testing Reference Implementations

You can manually test the reference implementations:

```bash
# Test with the integrated eval script
python eval/eval_integrated.py reference/app_with_sliding_window.py
python eval/eval_integrated.py reference/app_with_fixed_window.py

# Or test the standalone rate limiters
python eval/eval_example.py reference/token_bucket.py
python eval/eval_example.py reference/sliding_window.py
python eval/eval_example.py reference/fixed_window.py
```

## What This Demo Shows

1. **Real-world integration:** Agents modify existing code, not just write isolated modules
2. **Blind evaluation:** Supervisor designs tests before seeing any implementation
3. **Decision trails:** Each agent records choices (e.g., "used threading.Lock for thread safety")
4. **Bug detection:** The boundary bug in fixed window is caught automatically
5. **Parallel exploration:** All approaches run simultaneously, like CPU speculative execution

## The Boundary Bug Explained

Fixed window rate limiters have a classic problem:

```
Window 1: [00:00 - 01:00]
Window 2: [01:00 - 02:00]

Limit: 10 requests/minute
- At 00:59: Make 10 requests ✅ (all allowed, window 1)
- At 01:01: Make 10 requests ✅ (all allowed, window 2)
- Result: 20 requests in 2 seconds = 600 req/min burst!
```

Sliding window avoids this by tracking exact timestamps across the rolling 60-second window.

## File Structure

```
agentfleet-demo-ratelimiter/
├── app.py                              # Original app WITHOUT rate limiting (starting point)
├── requirements.txt                     # Flask dependency
├── reference/                          # Reference implementations (not used by agents)
│   ├── token_bucket.py                 # Standalone token bucket rate limiter
│   ├── sliding_window.py               # Standalone sliding window rate limiter
│   ├── fixed_window.py                 # Standalone fixed window rate limiter
│   ├── app_with_token_bucket.py        # Integrated: app.py + token bucket
│   ├── app_with_sliding_window.py      # Integrated: app.py + sliding window
│   └── app_with_fixed_window.py        # Integrated: app.py + fixed window
└── eval/
    ├── eval_example.py                 # Tests standalone rate limiters
    └── eval_integrated.py              # Tests rate limiting in app.py
```

## Expected Tournament Output

```
🥇 WINNER: Sliding window (94/100)
✅ All tests passed
📊 Metrics: correctness 1.0, simplicity 0.88, performance 0.8
🔍 Decisions: 3 recorded (thread safety, data structure, window calculation)

🥈 Token bucket (87/100)
✅ All tests passed
📊 Metrics: correctness 1.0, simplicity 0.75, performance 0.8

🥉 Fixed window (45/100)
❌ Failed boundary test
📊 Metrics: correctness 0.6, simplicity 0.9, performance 0.8
```
