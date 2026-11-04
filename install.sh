#!/bin/bash 

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME=notifier
EXEC_DIR="/opt/${SERVICE_NAME}"
EXEC_FILE="${EXEC_DIR}/app/app.py"

ENV_DIR="/etc/${SERVICE_NAME}"
ENV_FILE="${ENV_DIR}/.env"

SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

echo "Creating application root at ${EXEC_DIR}" 
sudo mkdir -p ${EXEC_DIR}
sudo chown master:master ${EXEC_DIR}

echo "Transfering application files" 
sudo cp -r ./app ${EXEC_DIR}

echo "Creating application environment and installing required modules"
python3 -m venv ${EXEC_DIR}/.venv
${EXEC_DIR}/.venv/bin/pip install -r ${ROOT_DIR}/requirements.txt

echo "Configuring environment"
sudo mkdir -p "${ENV_DIR}"

if [[ ! -f "${ENV_FILE}" ]]; then
    sudo install -m 600 \
        "${ROOT_DIR}/service/notifier.env.example" \
        "${ENV_FILE}"

    echo "Created ${ENV_FILE}"
    echo "IMPORTANT: Edit ${ENV_FILE} and configure your Telegram credentials."
else
    echo "Existing environment file preserved."
fi

sudo chmod 600 "${ENV_FILE}"

# Install systemd service
echo "Installing systemd service"

sudo install -m 644 \
    "${ROOT_DIR}/service/notifier.service" \
    "${SERVICE_FILE}"

# Enable and start service
echo "Registering and starting service"

sudo systemctl daemon-reload
sudo systemctl enable "${SERVICE_NAME}"

echo "Installation completed."
echo "To configure application tokens, edit environment file at ${ENV_FILE} and restart service"