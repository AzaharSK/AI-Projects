# Update local packages
sudo apt update && sudo apt upgrade -y

# Install Python3 pip and venv packages
sudo apt install python3-pip python3-venv build-essential -y

# Create a project directory and step into it
mkdir simple-rag-app && cd simple-rag-app

# Create a clean isolated virtual environment
python3 -m venv venv

# Activate your newly created virtual environment
source venv/bin/activate

# Upgrade pip inside the virtual environment
pip install --upgrade pip

# Install dependancy
pip install -r requirements.txt
