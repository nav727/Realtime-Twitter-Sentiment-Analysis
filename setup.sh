mkdir -p ~/.streamlit/

echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
[theme]\n\
base="dark"\n\
font="monospace"\n\
\n\
[client]\n\
showErrorDetails = False\n\
\n\
" > ~/.streamlit/config.toml
