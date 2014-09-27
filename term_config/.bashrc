source ~/.git-completion.bash
source ~/.git-prompt.sh

export PATH=/usr/local/git/bin:$PATH
export PS1='[\u@\h \W\[\033[01;35m\]$(__git_ps1 " (%s)")\[\033[00m\]]$ '

alias subl='/Applications/Sublime\ Text\ 2.app/Contents/SharedSupport/bin/subl'
alias ll='ls -lah'
alias gg='git status -s'
alias u='cd ..'
