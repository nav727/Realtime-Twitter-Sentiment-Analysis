mkdir -p ~/.streamlit/

echo "\
[server]
headless = true
port = $PORT
enableCORS = false

[theme]
base = dark
font = monospace

[client]
showErrorDetails = False
" > ~/.streamlit/config.toml
