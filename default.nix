#`{ nixpkgs ? import <nixpkgs> {} }:
{ pkgs ? import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/2b7c0dcdaab946153b0eaba5f2420f15ea27b0d6.tar.gz") {}}:

pkgs.mkShell {
  buildInputs = [
    #pkgs.direnv
    pkgs.python38
    pkgs.python38Packages.python-telegram-bot
    pkgs.terraform
    pkgs.awscli2
    pkgs.zip
  ];

  shellHook = ''
    echo "welcome to daytobase!"
    # eval "$(direnv hook bash)"

    # alias ls="ls --color=auto"
    # alias l="ls"
    # alias ll="ls -lha"
  '';
}
