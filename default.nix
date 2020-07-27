{ nixpkgs ? import <nixpkgs> {} }:

nixpkgs.mkShell {
  buildInputs = [
    # nixpkgs.direnv
    nixpkgs.mongodb-4_0
    nixpkgs.python38
    nixpkgs.python38Packages.python-telegram-bot
    nixpkgs.python38Packages.pymongo
  ];

  shellHook = ''
    # eval "$(direnv hook bash)"

    # alias ls="ls --color=auto"
    # alias l="ls"
    # alias ll="ls -lha"
  '';
}
