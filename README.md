# Getting Started

Set up a virtual environment at the root of the project:
```
python3 -m venv venv
```

Activate the virtual environment:
```
source venv/bin/activate
```

Install dependencies:
```
pip3 install -r requirements.txt
```

# Deploying

## Dreamhost
1. Follow the instructions to enable Passenger on the domain.
2. Install Python 3.7.6 following these instructions.
3. Install a virtual environment following these instructions.
4. Follow the instructions here to get Django going on Dreamhost, but instead of installing Django and creating a new project, `git clone` this repository and `pip3 install -r requirements.txt`