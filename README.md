# nba-archetypes-roster-builder

## Setup

If you are planning to run this **locally** and you are using macOS, first make sure that you have Homebrew and `pyenv` installed. You can quickly verify their prescence by running
```
which brew pyenv
```
in the terminal/command line.
#### Installing Homebrew and `pyenv`

Skip this stage if you have Homebrew and `pyenv` installed.

First, install Homebrew from https://brew.sh/, which is a package manager that helps you easily download packages in macOS/Linux/WSL environments.

Next, use Homebrew to install `pyenv`:
```
brew update
brew install openssl readline sqlite3 xz zlib tcl-tk
brew install pyenv
```
and then run the following in your terminal. Replace `~/.zshrc` with `~/.bash_profile` if your Mac is running `bash` rather than `zsh`. 
```
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init - zsh)"' >> ~/.zshrc
```
#### Setting up the virtual environment
Then, run
```
python3 -m venv .venv      
# create a new virtual environment named .venv
```
for a clean environment. Then, **activate** your environment:
```
source .venv/bin/activate
```
and install the required packages from requirements.txt.
```
pip install -r requirements.txt
```
This will give you a clean environment in which to work, so that everyone is working on the same thing. 

You can **deactivate** your environment by running:
```
deactivate
```
