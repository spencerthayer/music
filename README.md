# Learning Music via Code

The objective is to test and learn various programming languages and environments for coding music. This approach fosters creative expression and builds a deeper understanding of algorithmic and computational composition.

## TidalCycles Installation Overview

| Component | Purpose |
|-----------|---------|
| **SuperCollider** | Audio synthesis engine |
| **SuperDirt** | Sample playback & synths (runs in SuperCollider) |
| **GHCup** | Haskell toolchain manager |
| **GHC + Cabal** | Haskell compiler & package manager |
| **TidalCycles** | The pattern language itself |
| **Editor Plugin** | VS Code/Cursor extension for live coding |

---

### Step 1: Install SuperCollider

[1 tool called]

SuperCollider installed. Now let's install the Haskell toolchain (GHCup):

### Step 2: Install GHCup (Haskell Toolchain)

[1 tool called]

Excellent! Haskell toolchain installed. Now let's install TidalCycles:

### Step 3: Install TidalCycles

[1 tool called]

TidalCycles installed. Let's set up the shell environment and create a boot file for SuperDirt:

### Step 4: Configure Shell & Create BootTidal

[2 tools called]

Now let's create the SuperCollider startup file to install and boot SuperDirt:

### Step 5: Create SuperCollider Startup Files

[2 tools called]

Now let's create the VS Code/Cursor settings for the Tidal extension and an install script:

[2 tools called]

Let me check the VS Code extension marketplace for TidalCycles:

[1 tool called]

The TidalCycles VS Code extension is already installed. Here's your complete setup status:

---

## ✅ Installation Complete!

| Component | Status | Location |
|-----------|--------|----------|
| SuperCollider | ✅ Installed | `/Applications/SuperCollider.app` |
| GHCup | ✅ Installed | `~/.ghcup/` |
| GHC 9.6.7 | ✅ Installed | `~/.ghcup/bin/ghci` |
| Cabal | ✅ Installed | `~/.ghcup/bin/cabal` |
| TidalCycles | ✅ Installed | Global Haskell lib |
| VS Code Extension | ✅ Installed | `tidalcycles.vscode-tidalcycles` |
| BootTidal.hs | ✅ Created | `~/Desktop/music/BootTidal.hs` |
| Startup.scd | ✅ Created | `~/Library/Application Support/SuperCollider/` |

---

## 🎵 Remaining Manual Steps

### 1. Install SuperDirt (ONE TIME - in SuperCollider)

1. **Open SuperCollider** (from Applications)
2. **Open** the file `~/Desktop/music/install-superdirt.scd`
3. **Select this code** and press `Cmd+Enter` to run:

```supercollider
Quarks.checkForUpdates({Quarks.install("SuperDirt", "v1.7.3")});
```

4. **Wait** for download to complete (may take a few minutes)
5. **Recompile**: Press `Cmd+Shift+L` or menu **Language → Recompile Class Library**

### 2. Start SuperDirt (EVERY SESSION)

After recompiling, run this in SuperCollider (or it runs automatically from startup.scd):

```supercollider
SuperDirt.start
```

Or manually:
```supercollider
(
s.waitForBoot {
    ~dirt = SuperDirt(2, s);
    ~dirt.loadSoundFiles;
    s.sync;
    ~dirt.start(57120, 0 ! 12);
};
)
```

### 3. Use TidalCycles in Cursor/VS Code

1. **Open** `start.tidal` in Cursor
2. **Start Tidal**: Press `Cmd+Shift+P` → "TidalCycles: Start Tidal"
3. **Evaluate code**: Select a line/block and press `Cmd+Enter`

---

## 🚀 Quick Start Workflow

```bash
# Terminal 1: Open SuperCollider (or use the app)
open /Applications/SuperCollider.app

# In SuperCollider post window, you should see:
# "SuperDirt is running on port 57120"

# Then in Cursor:
# 1. Open start.tidal
# 2. Cmd+Shift+P → "TidalCycles: Start Tidal"  
# 3. Evaluate: startFull (Cmd+Enter)
```

---

## 🎛️ Supriya Music CLI

The `supriya_music` package provides a command-line interface for exploring SuperCollider synthesis through Python's Supriya library.

### Available Commands

```bash
# Display the main toolkit information
python -m supriya_music

# Get help for specific commands
python -m supriya_music hello --help

# Run the hello example with explanation (default)
python -m supriya_music hello

# Run the hello example without explanation
python -m supriya_music hello --no-explain

# Launch the TUI interface
python -m supriya_music tui
```

### VS Code Debug Configuration

The project includes a custom VS Code launch configuration that runs Python files as modules:

**Configuration**: "Python Debugger: Current File as Module"

- **Purpose**: Runs files using `python -m module_name` instead of `python file.py`
- **Benefits**: Proper module resolution and import handling
- **Usage**: Set breakpoints in any Python file and press `F5` to debug

### Example Workflow

1. **Open** any Python file in the `supriya_music/` directory
2. **Set breakpoints** where needed
3. **Press F5** to launch the debugger
4. The file will run as a module with proper import resolution

### CLI Features

- **Rich formatting**: Beautiful terminal output with syntax highlighting
- **Interactive explanations**: Step-by-step breakdowns of synthesis concepts
- **Modular design**: Easy to extend with new examples and commands
- **Educational focus**: Designed for learning Supriya and SuperCollider concepts
