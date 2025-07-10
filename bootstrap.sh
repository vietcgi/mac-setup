#!/usr/bin/env bash

# Bootstrap homebrew and ansible on MacOS
# Cannot be run as root, newer versions of homebrew will not run as root
# Changing directory ownership in /usr/local/bin for homebrew requires sudo
# The sudo chown command can be skipped with the -s option
# Password prompt will occur only if the owner change is not skipped

if [ $(id -u) = 0 ]; then
   echo Command cannot be run as root
   exit 1
fi

branch=
chown=true

function usage
{
    echo "Usage: "$0" [-b <branch>] [-c] [-d] [-h] [-s]"
    echo "-b <branch> - branch to use for git clone"
    echo "-c          - chown command will be skipped"
    echo "-h          - help by showing this usage"
}

while getopts ":b:cdhs" opt; do
  case ${opt} in
    b ) branch="--branch ${OPTARG}"
        echo Using git branch ${OPTARG}
      ;;
    c ) chown=false
        echo Skipping chown to user
      ;;
    h ) usage
        exit 0
      ;;
    : )
        echo Argument required: $OPTARG 1>&2
        usage
        exit 1
      ;;
    \? )
        echo Invalid option: $OPTARG 1>&2
        usage
        exit 1
      ;;
  esac
done

function error_trap
{
  local code="$?"
  local command="${BASH_COMMAND:-unknown}"
  echo "command [${command}] exited with code [${code}]" 1>&2
}
trap 'error_trap' ERR

# Script only runs on macOS
case "$OSTYPE" in
  darwin*)
    sw_vers
    ;;
  *)
    echo OS family is not supported
    exit 1
    ;;
esac

# Prepare /usr/local/bin as homebrew no longer runs under sudo

if ${chown}; then
    echo "Changing owner of directories in /usr/local/bin to" $(id -un)
    brewdirs=(
        Caskroom
        Cellar
        Homebrew
        Frameworks
        bin
        doc
        etc
        etc/bash_completion.d
        include
        lib
        lib/pkgconfig
        libexec
        opt
        sbin
        share
        share/doc
        share/info
        share/man
        share/man/man1
        share/man/man3
        share/man/man5
        share/man/man8
        share/zsh
        share/zsh/site-functions
        var
        var/homebrew
        var/homebrew/linked
        var/homebrew/locks
    )
    cd /usr/local
    sudo mkdir -p -m 0755 ${brewdirs[*]}
    sudo chown -R $(id -un):$(id -gn) ${brewdirs[*]}
    cd ${OLDPWD}
else
    echo "Skipping change owner of directories in /usr/local/bin to" $(id -un)
fi

# Install homebrew
if command -v brew >& /dev/null; then
    echo Homebrew is installed
else
    echo Installing Homebrew
    if ! /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"; then
        echo "Failed to install Homebrew"
        exit 1
    fi
fi
if [[ $(uname -m) == 'arm64' ]]; then
  echo M1 Mac detected
  # Only add to .zprofile if not already present
  if ! grep -q "eval.*opt/homebrew.*shellenv" "$HOME/.zprofile" 2>/dev/null; then
    echo 'eval $(/opt/homebrew/bin/brew shellenv)' >> $HOME/.zprofile
  fi
  eval $(/opt/homebrew/bin/brew shellenv)
else 
  echo Intel Mac detected
  # Only add to .zprofile if not already present
  if ! grep -q "eval.*usr/local.*shellenv" "$HOME/.zprofile" 2>/dev/null; then
    echo 'eval $(/usr/local/bin/brew shellenv)' >> $HOME/.zprofile
  fi
  eval $(/usr/local/bin/brew shellenv)
fi


# Install developer tools if needed, newer versions of homebrew already do this
if xcode-select -p >& /dev/null; then
    echo Command Line Tools are installed
else
    sw_vers=$(sw_vers -productVersion | awk -F "." '{print $2}')
    if [[ "${sw_vers}" -ge 9 ]]; then
        # Temporary file causes softwareupdate to list the Command Line Tools
        clt_file="/tmp/.com.apple.dt.CommandLineTools.installondemand.in-progress"
        touch "${clt_file}"
        if clt_update=$(softwareupdate -l | grep "\*.*Command Line"); then
            echo Installing update to Command Line Tools
            clt_pkg=$(echo "${clt_update}" | head -n 1 | awk -F"* " '{print $2}')
            if ! softwareupdate --install --verbose "${clt_pkg}" ; then
                echo Install of Command Line Tools failed
                echo Try running command "xcode-select --install" before running this script
                exit 1
            fi
        else
            echo Update to Command Line Tools not found
            echo Try running command "xcode-select --install" before running this script
            exit 1
        fi
        rm -f "${clt_file}"
    else
        echo Not installing Command Line Tools for MacOS prior to version 10.9
        echo Try running command "xcode-select --install" before running this script
        exit 1
    fi
fi

# Command exit value checking not needed from this point
set -o errexit -o errtrace

# Install ansible
if command -v ansible >& /dev/null; then
    echo Ansible is installed
else
    echo Installing Ansible
    if ! brew install ansible; then
        echo "Failed to install Ansible"
        exit 1
    fi
    echo Ansible installation complete
fi
echo -n "Version: "
ansible --version

echo Installing the Ansible requirements
if ! ansible-galaxy install -r requirements.yml --force; then
    echo "Failed to install Ansible requirements"
    exit 1
fi
echo Ansible requirements installation complete

echo Install Ansible Playbook
# Use sudo with timeout to avoid multiple password prompts
# sudo -v extends the timeout for subsequent sudo commands
sudo -v
if ! ansible-playbook -i inventory main.yml --become; then
    echo "Ansible playbook execution failed"
    exit 1
fi
echo "Mac setup completed successfully!"

