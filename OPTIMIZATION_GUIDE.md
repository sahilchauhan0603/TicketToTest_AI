# ⚡ Free Tier Optimization Guide

> **TL;DR**: System auto-handles 5 requests/minute limit. First ticket: ~60s. Same ticket again: ~3s (cached). Different tickets: ~60s each.

---

## 📊 Your Limits

**Gemini API Free Tier:**
- 5 requests/minute (RPM) ⚠️
- 250K tokens/minute (TPM) ✅
- 20 requests/day (RPD) ✅

**Your system uses 5 API calls per ticket** (1 per agent), so processing is auto-spaced.

---

## ✅ What's Optimized

1. **Auto-Spacing**: 12 seconds between agents (60s ÷ 5 = 12s)
2. **Caching**: Identical requests = 0 API calls
3. **Retry Logic**: Auto-retry on 429 errors (3 attempts)
4. **Progress Display**: Shows wait times in UI

---

## 🚀 How to Use

### First Run:
```bash
streamlit run app.py
```
- Enter API key in sidebar
- Enable caching ✅
- Process ticket: **~60 seconds**

### Same Ticket Again:
- Process again: **~3 seconds** (0 API calls, fully cached)

### Different Tickets:
- Auto-spaced: **~60 seconds each**

---

## 💡 Pro Tips

**Maximize Free Tier:**
- ✅ Keep caching enabled (sidebar)
- ✅ Test with same ticket (free retries)
- ✅ Process one ticket at a time
- ❌ Don't disable caching
- ❌ Don't restart app repeatedly

**Clear Cache When Needed:**
```powershell
Remove-Item -Recurse -Force .api_cache
```

---

## 📈 Performance

| Scenario | Time | API Calls | Cache |
|----------|------|-----------|-------|
| First ticket | ~60s | 5 | 0% |
| Same ticket | ~3s | 0 | 100% |
| Daily max | ~20 min | 20 tickets | Varies |

---

## 🆘 Troubleshooting

**Still getting 429 errors?**
```powershell
# Wait 60 seconds, then restart
Start-Sleep -Seconds 60
streamlit run app.py
```

**Cache not working?**
```powershell
# Delete and let it rebuild
Remove-Item -Recurse -Force .api_cache
```

**Want faster processing?**
- Upgrade to paid tier: Gemini 1.5 Flash = 2000 RPM ($0.075/1M tokens)

---

## ⚙️ Settings

**In .env file:**
```bash
LLM_MODEL=gemini-3-flash-preview
LLM_TEMPERATURE=0.3
GOOGLE_API_KEY=your_key_here
```

**Cache TTL** (default: 1 hour):
Edit `agents/orchestrator.py`:
```python
self.api_cache = get_api_cache(ttl=7200)  # 2 hours
```

---

## 🎯 Expected Behavior

**Normal (First Run):**
```
📖 Ticket Reader (2s) → ⏱️ wait 12s →
🏗️ Context Builder (2s) → ⏱️ wait 12s →
🎯 Strategy (2s) → ⏱️ wait 12s →
✏️ Generator (3s) → ⏱️ wait 12s →
🔍 Auditor (2s) → ✅ Done! (~60s total)
```

**Cached (Repeat Run):**
```
All agents → ✅ Done! (~3s total, 0 API calls)
```

---

**Your system is ready! Process tickets at ~1 per minute on free tier.** 🎉

## ✅ Optimizations Implemented

### 1. **Rate Limiter** (`utils/rate_limiter.py`)
- Tracks API calls in a sliding 60-second window
- Automatically pauses when limit would be exceeded
- Calculates precise wait time before next request
- Thread-safe for concurrent operations

**How it works:**
```python
# Before each API call
rate_limiter.wait_if_needed()  # Pauses if needed
# Make API call
```

### 2. **Response Caching** (`utils/api_cache.py`)
- Caches API responses for 1 hour (configurable)
- Identical requests reuse cached responses
- File-based cache survives app restarts
- Reduces redundant API calls significantly

**Benefits:**
- Re-running the same ticket uses **0 API calls** (all cached)
- Similar tickets may benefit from cached components
- Testing/debugging doesn't burn through quota

### 3. **Updated Agent Architecture**
All agents now support:
- Rate limiting (automatic wait before API calls)
- Response caching (check cache before API call)
- Graceful degradation (continue if cache available)

### 4. **Enhanced Progress Display**
The UI now shows:
- Current agent being processed
- Rate limit wait times (when paused)
- Processing time estimates
- Cache hit indicators

## 🚀 Usage Guide

### Running the Optimized System

1. **First Ticket** (Full API Usage):
   - Uses all 5 API calls
   - Total time: ~60 seconds (includes rate limit waits)
   - All responses cached

2. **Same Ticket Again** (Zero API Usage):
   - Uses 0 API calls (all cached)
   - Total time: ~2-3 seconds
   - No rate limits hit

3. **Multiple Different Tickets**:
   - System auto-pauses between batches
   - Processes 1 ticket per minute
   - Shows clear wait times in UI

### Best Practices

#### ✅ DO:
- **Enable caching** in sidebar settings
- **Test with same ticket** first to verify caching works
- **Process tickets sequentially** during development
- **Wait for rate limit info** displayed in UI
- **Clear cache** (delete `.api_cache/` folder) if responses seem stale

#### ❌ DON'T:
- Try to process multiple tickets simultaneously
- Disable caching unless necessary
- Restart the app repeatedly (loses cache warmth)
- Use different LLM_MODEL settings (cache won't match)

## 📈 Expected Performance

### With Free Tier (5 RPM):
| Scenario | API Calls | Time | Cache Hits |
|----------|-----------|------|------------|
| First ticket | 5 | ~60s | 0% |
| Same ticket again | 0 | ~3s | 100% |
| 2nd different ticket | 5 | ~120s | 0% |
| 3rd different ticket | 5 | ~180s | 0% |

### Tips for Maximizing Throughput:
1. **Batch similar tickets** - may benefit from partial cache hits
2. **Use cache** - re-testing same tickets is free
3. **Plan ahead** - process tickets when you can wait
4. **Monitor sidebar** - shows cache stats and rate limit status

## 🔧 Advanced Configuration

### Adjusting Cache TTL
Edit `agents/orchestrator.py`:
```python
self.api_cache = get_api_cache(ttl=7200)  # 2 hours instead of 1
```

### Clearing Cache
```bash
# PowerShell
Remove-Item -Recurse -Force .api_cache

# Or manually delete the .api_cache folder
```

### Checking Cache Stats
The system tracks:
- Total cached entries
- Valid vs expired entries
- Cache hit rate

## 🆙 Upgrading Options

If you need more throughput:

### Option 1: Upgrade to Paid Tier
- Gemini 1.5 Flash: 2000 RPM ($0.075 / 1M tokens)
- Gemini 1.5 Pro: 360 RPM ($1.25 / 1M tokens)

### Option 2: Use Different Model Tiers
- Keep strategy/planning on Flash (cheaper)
- Use Pro only for test generation (quality)

### Option 3: Optimize Agent Calls
Potential improvements:
- Combine agents where possible
- Use smaller prompts
- Batch test generation

## 📝 Monitoring Your Usage

1. **Check Google AI Studio**: https://ai.dev/rate-limit
2. **Watch UI messages**: Shows wait times and rate limit info
3. **Cache folder size**: Indicates how much is cached
4. **Processing times**: Faster = more cache hits

## ❓ Troubleshooting

### Still getting 429 errors?
- Wait 60 seconds before retrying
- Check if cache is enabled
- Verify `.api_cache` folder exists and is writable

### Cache not working?
- Check file permissions on `.api_cache/`
- Verify prompts are identical (model, temperature, etc.)
- Clear and rebuild cache

### Slow processing?
- Expected with free tier (1 ticket per minute)
- Enable caching to speed up repeated requests
- Consider upgrading tier if needed

## 📚 Files Modified

The optimization touched these files:
- ✅ `utils/rate_limiter.py` - NEW: Rate limiting logic
- ✅ `utils/api_cache.py` - NEW: Response caching
- ✅ `agents/orchestrator.py` - Updated: Initialize rate limiter & cache
- ✅ `agents/ticket_reader.py` - Updated: Use rate limiter & cache
- ✅ `agents/context_builder.py` - Updated: Use rate limiter & cache
- ✅ `agents/test_strategy.py` - Updated: Use rate limiter & cache
- ✅ `agents/test_generator.py` - Updated: Use rate limiter & cache
- ✅ `agents/coverage_auditor.py` - Updated: Use rate limiter & cache
- ✅ `app.py` - Updated: UI improvements, rate limit info

## 🎯 Summary

The system is now **optimized for free tier usage**:
- ✅ Respects 5 RPM limit automatically
- ✅ Caches responses to minimize calls
- ✅ Shows clear progress and wait times
- ✅ Handles rate limits gracefully
- ✅ Maximizes free tier efficiency

**Expected behavior**: 
- First run: Uses 5 calls, takes ~60s (with pauses)
- Subsequent runs: Cached, takes ~3s, 0 calls
- Different tickets: 1 per minute, auto-pauses
