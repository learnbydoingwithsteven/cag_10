# App 10: Fact Checker

**Tool-use CAG**

This application verifies claims by using external tools (e.g., Search, Wikipedia).

## Features
- **Claim Detection**: Identifies factual claims in text.
- **Evidence Gathering**: Uses tools to find supporting/refuting evidence.
- **Verdict Generation**: determining if a claim is True, False, or Unverifiable.

## Status
- **Backend**: Verified Running (Port 8010).
- **Frontend**: Failed to start (Port 3010) due to environment issues.

## Verification
Verified Backend API docs at `http://localhost:8010/docs`.
> Note: Screenshot unavailable due to temporary resource constraints. Verified via curl:
```bash
$ curl -I http://localhost:8010/docs
HTTP/1.1 200 OK
```
