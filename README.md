# Personal Website

Note: this project has moved [here](https://github.com/aidaco/www-min)

Source for my personal site.

## Features
- Public & protected pages.
- Live demonstration.
- Build as standalone pyz executable.
- Auto-upgrade via webhook, even when built as pyz.

## Setup
- Note: your mileage my vary.
- Clone & install deps
  - Requires git, npm, python, poetry
  ```
  $git clone https://github.com/aidaco/www
  $cd www
  $python -m poetry install
  ```
- Edit config
  `$python -m server initconfig`
  - Can generate a password hash with `$python -m server hashpwd PASSWORD`

- Build & run
  - Standard
    ```
    $./dev.py buildstatic
    $python -m server run
    ```

  - pyz
    ```
    $./dev.py buildpyz
    $./aidan.software.pyz
    ```
