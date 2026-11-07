mkdir -p ~/b3lib && cd ~/b3lib && pip install --target ~/b3lib/pk blake3 2>&1 | tail -3
PYTHONPATH=~/b3lib/pk python3 -c "import blake3; print(blake3.blake3(b'abc').hexdigest())"
