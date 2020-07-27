# Daytobase

Notes are not documents, they are *messages*.

Daytobase is a [Telegram](https://telegram.org/) bot that records whatever you send it to a database. You can review records by hashtags, search by text and export them to CSV. Try it [here](https://telegram.me/daytobasebot)!

## How to set up a dev & deploy environment

Note: For users the deployment story will be simpler. The setup here is only more involved because it makes development easier.

### Set the necessary variables

Go into the AWS console - My Security Credentials - Access keys, and create a new access key (or recover an old one).

Create a file called `.envrc` with the following content:

```bash
use nix  # comment out if you don't use Nix.

export AWS_ACCESS_KEY_ID="<YOUR_ACCESS_KEY_HERE>"
export AWS_SECRET_ACCESS_KEY="<YOUR_SECRET_HERE>"
```

Replace the placeholders with your actual config values and secrets.

### Option A: Install Nix and direnv

This will just install all the necessary cli tools and Python dependencies for you. No need to even create a `venv`, plus it's reproducible!

#### Install Nix

Follow the instructions at [nixos.org](https://nixos.org/download.html). It's mostly

```bash
curl -L https://nixos.org/nix/install | sh
```

You will need to restart your shell. See if it worked by typing `nix-env --version`.

#### Install direnv

Install [direnv](https://direnv.net/), and follow the instructions so that it hooks into your shell.

Do the necessary shell restarting, and allow the contents of your `.envrc` with

```bash
direnv allow
```

If you see a shiny `Daytobase` logo, then that's it. All your dependencies are in scope whenever you `cd` into the project directory.

### Option B: Be a caveman

1. Install dependencies like the AWS CLI, Terraform, as well as the Python libraries (with `venv` or whatever).
2. Get the settings by doing `source .envrc`.
3. Cry when Python breaks.
