# { nixpkgs ? import <nixpkgs> {} }:
{ pkgs ? import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/2b7c0dcdaab946153b0eaba5f2420f15ea27b0d6.tar.gz") {}}:

with pkgs; mkShell {
  buildInputs = [
    # direnv
    toilet
    python38
    python38Packages.pip
    terraform
    awscli2
    jq
  ];

  shellHook = ''
    toilet Daytobase -f future --gay
    alias tf=terraform
    # eval "$(direnv hook bash)"
  '';
}
