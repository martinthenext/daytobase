# { nixpkgs ? import <nixpkgs> {} }:
{ pkgs ? import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/2c0034d5fbcb1b6b511a2369329a2446c84bf884.tar.gz") {}}:

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
