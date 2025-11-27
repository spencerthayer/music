# Strudel Environment Setup for Gemini

This guide outlines the steps to set up a development environment for Strudel, a live coding environment for musical patterns, specifically for use with the Gemini CLI.

## 1. Project Overview

Strudel is a JavaScript-based live coding environment inspired by TidalCycles. It allows users to create and manipulate musical patterns using code. The project is structured as a monorepo containing various packages (core, web, desktop, etc.).

## 2. Prerequisites

Before you begin, ensure you have the following installed on your system:

*   **Node.js**: It's recommended to use the version specified in `.nvmrc` (if present) or a recent LTS version.
*   **pnpm**: Strudel uses pnpm for package management. Install it globally: `npm install -g pnpm`
*   **Rust and Cargo**: Required for building the Tauri desktop application. Follow the instructions on the [Rust website](https://www.rust-lang.org/tools/install) to install `rustup`, then install the necessary toolchains.

## 3. Getting Started

1.  **Clone the repository:**
    ```bash
    git clone https://codeberg.org/uzu/strudel.git
    cd strudel-music/strudel
    ```
    (Note: Replace `https://codeberg.org/uzu/strudel.git` with the actual repository URL if different.)

2.  **Install dependencies:**
    ```bash
    pnpm install
    ```

## 4. Running the Development Environment

Strudel is a monorepo with several packages. Here are some common ways to run different parts of the project:

*   **Website (Astro):**
    ```bash
    pnpm --filter website dev
    ```
    This will start the Astro development server for the main Strudel website.

*   **Web REPL (e.g., `packages/web`):**
    You can run specific web-based REPLs or examples. For instance, to run the `packages/web` development server:
    ```bash
    pnpm --filter @strudel/web dev
    ```

*   **Tauri Desktop Application:**
    ```bash
    pnpm --filter strudel-tauri tauri dev
    ```
    This will build and run the desktop application in development mode.

## 5. Useful Commands

*   **Build all packages:**
    ```bash
    pnpm build
    ```

*   **Run tests:**
    ```bash
    pnpm test
    ```

*   **Run linting:**
    ```bash
    pnpm lint
    ```

## 6. Project Structure (Relevant to Gemini)

The Strudel project has a monorepo structure. Key directories and files include:

*   `packages/`: Contains all the individual Strudel packages (e.g., `core`, `web`, `midi`, `tauri`).
*   `website/`: The main Strudel website built with Astro.
*   `examples/`: Various examples demonstrating Strudel's capabilities.
*   `strudel-music.code-workspace`: VS Code workspace file.
*   `pnpm-workspace.yaml`, `lerna.json`, `package.json`: Monorepo configuration and main project dependencies.

When working with Gemini, you can use commands like `list_directory`, `read_file`, `search_file_content`, and `glob` to navigate and understand this structure.
