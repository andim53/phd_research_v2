---
name: api-rate-limiter
description: Use for API quota 429 errors; adds backoff retry logic.
---

# API Rate-Limit Handling and Auto-Retry
Use when an automated process or cron job encounters 429 Rate Limit errors or model quotas. This pattern uses a simple wait-and-retry strategy to ensure long-running tasks eventually complete.

## Implementation Pattern
When running a task that might hit quota limits, wrap the core execution in a retry logic that uses exponential backoff and a minimum wait time.

### Example Retry Logic
```python
import time
import random

def run_with_retry(fn, max_retries=5):
    attempt = 0
    while attempt < max_retries:
        try:
            return fn()
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                sleep_time = (60 * (attempt + 1)) + random.uniform(0, 10)
                print(f"Rate limit hit. Waiting {sleep_time:.0f} seconds...")
                time.sleep(sleep_time)
                attempt += 1
            else:
                raise e
    raise Exception("Max retries exceeded")
```

## Pitfalls
- Do not use this for real-time interactive tasks where the user is waiting.
- Always log the retry attempts so you can monitor if the job is constantly hitting limits.
- If a job hits the limit consistently, consider lowering the frequency of the cron job or chunking the work into smaller pieces.
