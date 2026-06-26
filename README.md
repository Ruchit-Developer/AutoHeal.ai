<div align="center">
  <img src="main_logo.svg" alt="AutoHeal.ai Logo" width="250"/>
  <h1>AutoHeal.ai | Universal Engine v3.0</h1>
</div>

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![AI Models](https://img.shields.io/badge/Providers-OpenAI%20%7C%20Gemini%20%7C%20Local-8A2BE2.svg)](#)
[![Renderer](https://img.shields.io/badge/Renderer-Selenium_Headless-43B02A.svg)](https://www.selenium.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**AutoHeal.ai** is an autonomous, model-agnostic visual repair engine. It acts as an AI-powered UX Architect that programmatically renders broken HTML/CSS, captures the visual context, interfaces with large multimodal models (GPT-4o, Gemini 2.5, or Local Vision Models), and securely injects the optimized layout back into the local filesystem.

## 🚀 The V3.0 Universal Upgrade
AutoHeal is no longer bound to a single API. By dynamically converting DOM screenshots to raw Base64, the engine can hot-swap between providers in real-time.

*   **Google Engine:** Native support for `gemini-2.5-pro` and `flash`.
*   **OpenAI Engine:** Native support for `gpt-4o`.
*   **Open-Source Engine:** Plug into local/private networks (Ollama, LM Studio, Groq) using standard OpenAI-compatible endpoints.

## 🛠 Core Features

*   **`/build` (Zero-to-One Generation):** Type `/build "A crypto dashboard"` and the engine generates base HTML from scratch, then automatically pipes it into the visual healing loop for premium glassmorphism styling.
*   **`--ref` (Figma-to-Code):** Provide a target design mock (e.g., `/heal index.html --ref figma.png`). The engine cross-references the current DOM state against the image and rewrites the CSS to match the designer's intent perfectly.
*   **`--dir` (Macro-Crawling):** Supply a directory to the engine. It recursively boots a headless browser for every file, unifying the design system across the entire codebase without manual intervention.
*   **`--react` (Framework Compiler):** Add the `--react` flag, and AutoHeal runs a dual-pass compilation, exporting your fixed HTML/CSS directly into a production-ready `React.jsx` component styled with Tailwind.

## Quick Start

### Prerequisites
- Python 3.10+
- Google Chrome & ChromeDriver

### Installation

```bash
git clone https://github.com/yourusername/AutoHeal.ai.git
cd AutoHeal.ai

# Initialize virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies (Includes OpenAI Python Bridge)
pip install -r requirements.txt
```

### Configuration
AutoHeal enforces a Zero-Trust security model. Authentication keys are dynamically loaded via `.env`.

```bash
cp .env.example .env
```
Edit your `.env` to include the providers you want to use:
```env
GEMINI_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
# For Local Models (Ollama, etc.):
OPENSOURCE_BASE_URL=http://localhost:11434/v1
OPENSOURCE_MODEL_NAME=llama3.2-vision
```

## Usage Reference

To initialize the Interactive Developer Shell:
```bash
python agent.py
```

### CLI Commands
| Command | Parameter | Description |
| :--- | :--- | :--- |
| `/build` | `"prompt"` | Generates raw HTML from text and visually heals it. |
| `/heal` | `[file]` | Initiates the visual capture and refactoring pipeline. |
| `/provider`| `google`\|`openai`\|`opensource` | Hot-swaps the underlying inference engine on the fly. |
| `--ref` | `[image_path]` | Flag used with `/heal` to enforce Figma-to-Code styling. |
| `--dir` | `[folder_path]` | Flag used with `/heal` for folder-wide macro-crawling. |
| `--react` | none | Flag used with `/heal` to compile output to JSX/Tailwind. |
| `/status` | none | Outputs active provider and system configuration. |

## Security Model
*   **No Hardcoded Secrets:** Strict environment variable isolation.
*   **API Resilience:** Implements standard Cloud exponential backoff strategies to gracefully handle rate limiting during Macro-Crawling (`--dir`).
*   **Sandboxed Output:** Modified components are safely written to `/output` to prevent destructive overwrites of target source code.

---
*Maintained by Ruchit. Designed for high-velocity engineering environments.*
