mkdir -p ~/.streamlit/

echo "\
[server]
headless = true
port = 9200
enableCORS = false

[theme]
base = 'dark'
font = 'monospace'

[client]
showErrorDetails = false
" > ~/.streamlit/config.toml
