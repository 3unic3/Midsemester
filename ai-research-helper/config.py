"""
Model configuration — swap models here easily.
All available models on this machine:
  gpt-oss:120b-cloud       (most capable, slower)
  devstral-small-2:24b-cloud
  ministral-3:8b-cloud     (fastest)
"""

# Used for Coordinator + Synthesis (need strong reasoning)
STRONG_MODEL = "gpt-oss:120b-cloud"

# Used for per-agent summarization (4 parallel calls, speed matters)
FAST_MODEL = "ministral-3:8b-cloud"
