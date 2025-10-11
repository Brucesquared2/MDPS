# GCP Modules Organizer

## Overview
The GCP Modules Organizer is a project designed to acquire and organize Google Cloud Platform (GCP) modules from GitHub into a modular project structure. This tool automates the process of fetching GCP modules, detecting their types, and organizing them according to a predefined project structure.

## Project Structure
The project follows a modular architecture, with the following key directories and files:

- **src/**: Contains the source code for the application.
  - **main.ts**: Entry point of the application.
  - **services/**: Contains service classes for GitHub interactions and module organization.
  - **models/**: Defines interfaces for GCP modules and project structure.
  - **utils/**: Utility functions for file and Git operations.
  - **config/**: Configuration settings for the application.

- **scripts/**: Contains shell scripts for organizing modules and setting up the project environment.
  - **organize.sh**: Automates the organization of GCP modules.
  - **setup.sh**: Sets up the project environment and installs dependencies.

- **templates/**: Contains templates for GCP modules.
  - **module-template/**: Template files for each GCP module, including `package.json` and `index.ts`.

- **package.json**: Configuration file for npm, listing dependencies and scripts.

- **tsconfig.json**: TypeScript configuration file specifying compiler options.

## Setup Instructions
1. Clone the repository:
   ```
   git clone <repository-url>
   cd gcp-modules-organizer
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Configure your GitHub credentials and project paths in `src/config/settings.ts`.

4. Run the setup script to prepare the environment:
   ```
   ./scripts/setup.sh
   ```

## Usage
To acquire and organize GCP modules, run the following command:
```
./scripts/organize.sh
```

This will fetch the modules from GitHub, detect their types, and organize them into the specified project structure.

## Contribution Guidelines
Contributions are welcome! Please follow these steps to contribute:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them.
4. Push your branch and create a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.