# Troubleshooting callscope

This document contains standard troubleshooting steps for common issues encountered when integrating or running `callscope`.

## Common Issues

### 1. Format Detection Errors
If `callscope` fails to automatically detect your transcript format, pass the format parameter explicitly:
```python
analyze(transcript, fmt="vapi")  # or "text"
```

### 2. Regex Customization
If your signals are not being picked up correctly, make sure your regex compiles properly:
```python
from callscope.signals import _compile
# Check if the regex pattern matches
```
