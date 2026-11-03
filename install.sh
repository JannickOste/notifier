#!/bin/bash 

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXEC_DIR="/opt/notifier"
ENV_DIR="/etc/notifier/.env"

echo "Creating application root at ${EXEC_DIR}" 
sudo mkdir -p ${EXEC_DIR}
sudo chown master:master ${EXEC_DIR}

echo "Transfering application files" 
sudo cp -r ./app ${EXEC_DIR}

echo "Creating application environment and installing required modules"
python3 -m venv ${EXEC_DIR}/.venv
${EXEC_DIR}/.venv/bin/pip install -r requirements.txt