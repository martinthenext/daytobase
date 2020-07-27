# { nixpkgs ? import <nixpkgs> {} }:
{ pkgs ? import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/2b7c0dcdaab946153b0eaba5f2420f15ea27b0d6.tar.gz") {}}:

with pkgs; mkShell {
  buildInputs = [
    # direnv
    toilet
    python38
    python38Packages.python-telegram-bot
    terraform
    awscli2
    zip
    jq
  ];

  shellHook = ''
    toilet Daytobase -f future --gay
    # eval "$(direnv hook bash)"
  '';
}
