# 1. Install Python Dependencies
pip install -r requirements.txt

# 2. Install Node Dependencies
npm i -g cline @qodo/command

# 3. Setup Crawl4AI browser
crawl4ai-setup

# 4. Check for Ollama
if (Get-Command ollama -ErrorAction SilentlyContinue) {
    Write-Host "Ollama found! Pulling models..."
    ollama pull qwen2.5-coder:32b
    ollama pull deepseek-v3
} else {
    Write-Host "Please install Ollama from https://ollama.com"
}

Write-Host "Paradise Stack Ready. Run 'docker-compose up -d' to start observability."
