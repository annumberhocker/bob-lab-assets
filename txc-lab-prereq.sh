#!/usr/bin/env bash

set -euo pipefail

rm -rf txc-lab
unzip txc-lab.zip
rm -r __MACOSX

if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew not found. Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  echo >> /home/itzuser/.bashrc
  echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv bash)"' >> /home/itzuser/.bashrc
  eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv bash)"
  sudo dnf group install 'Development Tools' && sudo dnf install bubblewrap
else
  echo "Homebrew already installed."
fi

echo "Installing lab prerequisites with Homebrew..."
brew install python@3.12 uv
brew install node bc 
brew install openjdk maven

echo ""
echo "Prerequisite installation complete."
echo "Next steps:"
echo "  - Agentic Lab: cd txc-lab/agentic-lab && make setup && make init-db"
echo "  - Data Science Lab: cd txc-lab/datascience-lab/lab && uv venv && source .venv/bin/activate"
echo "  - Java Upgrade: cd txc-lab/java-upgrade && mvn test"

