nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu --format=csv
nvcc --version | tail -2
lscpu | grep -E "Model name|Flags" | cut -c1-200
uptime
python3 -c "import flint" 2>&1 | tail -1
free -g | head -2
