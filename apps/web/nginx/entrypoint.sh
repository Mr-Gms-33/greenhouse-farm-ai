#!/bin/sh
set -eu

CONFIG="/etc/nginx/conf.d/default.conf"

if [ -n "${API_PROXY_URL:-}" ]; then
  cat > "$CONFIG" <<EOF
server {
  listen 80;
  server_name _;
  root /usr/share/nginx/html;
  index index.html;

  location / {
    try_files \$uri /index.html;
  }

  location /api/ {
    proxy_pass ${API_PROXY_URL};
    proxy_set_header Host \$host;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto \$scheme;
  }
}
EOF
else
  cat > "$CONFIG" <<'EOF'
server {
  listen 80;
  server_name _;
  root /usr/share/nginx/html;
  index index.html;

  location / {
    try_files $uri /index.html;
  }
}
EOF
fi

exec nginx -g "daemon off;"
