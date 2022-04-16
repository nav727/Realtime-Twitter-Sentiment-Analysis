mkdir -p ~/.streamlit/

echo "\
[server]
headless = true
port = $PORT
enableCORS = false

[theme]
base = 'dark'
font = 'monospace'

[client]
showErrorDetails = false
" > ~/.streamlit/config.toml
