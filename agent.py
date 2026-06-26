import os
import sys
import time
import re
import argparse
import base64
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich import box

# Universal AI Bridge Imports
try:
    from google import genai
    from openai import OpenAI
except ImportError:
    pass # Handled gracefully if user hasn't run requirements.txt yet

console = Console()

ASCII_LOGO = """[bold cyan]
 █████╗ ██╗   ██╗████████╗ ██████╗ ██╗  ██╗███████╗ █████╗ ██╗     
██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗██║  ██║██╔════╝██╔══██╗██║     
███████║██║   ██║   ██║   ██║   ██║███████║█████╗  ███████║██║     
██╔══██║██║   ██║   ██║   ██║   ██║██╔══██║██╔══╝  ██╔══██║██║     
██║  ██║╚██████╔╝   ██║   ╚██████╔╝██║  ██║███████╗██║  ██║███████╗
╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝[/bold cyan]
[dim white]Autonomous Interface Repair Protocol | Universal Engine v3.0[/dim white]
"""

def print_welcome_header():
    os.system('cls' if os.name == 'nt' else 'clear')
    console.print(ASCII_LOGO)
    console.print("[dim]Type [bold white]/help[/bold white] to see available commands.[/dim]\n")

def print_help():
    table = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED, border_style="cyan")
    table.add_column("Command", style="bold cyan", width=25)
    table.add_column("Description", style="white")
    
    table.add_row("/build [prompt]", "Zero-to-One: Generate base HTML and heal it in one pass")
    table.add_row("/heal [file]", "Capture and heal a specific HTML file")
    table.add_row("/heal --dir [folder]", "Macro-Crawling: Heal all HTML files in a directory")
    table.add_row("  --ref [image.png]", "Multimodal Reference: Use an image as a design target")
    table.add_row("  --react", "Framework Compiler: Export healed UI as React/Tailwind")
    table.add_row("/provider [name]", "Hot-swap the AI Engine (google, openai, opensource)")
    table.add_row("/status", "Display current system configuration")
    table.add_row("/exit", "Terminate the AutoHeal session")
    
    console.print(table)

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def call_universal_llm_with_backoff(prompt, image_paths, provider, status_msg):
    max_retries = 3
    base_delay = 10
    
    for attempt in range(1, max_retries + 1):
        with console.status(f"[bold yellow]{status_msg} (Attempt {attempt}/{max_retries})...[/bold yellow]", spinner="bouncingBar"):
            try:
                load_dotenv()
                
                # --- GOOGLE GEMINI ROUTING ---
                if provider == "google":
                    api_key = os.environ.get("GEMINI_API_KEY")
                    if not api_key: raise ValueError("GEMINI_API_KEY missing in .env")
                    client = genai.Client(api_key=api_key)
                    contents = []
                    
                    for img in image_paths:
                        uploaded_file = client.files.upload(file=img)
                        contents.append(uploaded_file)
                        
                    contents.append(prompt)
                    response = client.models.generate_content(
                        model="gemini-2.5-pro",
                        contents=contents
                    )
                    return response.text.strip()
                    
                # --- OPENAI & OPEN-SOURCE ROUTING ---
                elif provider in ["openai", "opensource"]:
                    api_key = os.environ.get("OPENAI_API_KEY") if provider == "openai" else os.environ.get("OPENSOURCE_API_KEY", "dummy-key")
                    base_url = None if provider == "openai" else os.environ.get("OPENSOURCE_BASE_URL", "http://localhost:11434/v1")
                    model_name = "gpt-4o" if provider == "openai" else os.environ.get("OPENSOURCE_MODEL_NAME", "llama3.2-vision")
                    
                    if not api_key and provider == "openai": raise ValueError("OPENAI_API_KEY missing in .env")
                    
                    client = OpenAI(api_key=api_key, base_url=base_url)
                    messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
                    
                    for img in image_paths:
                        base64_img = encode_image_to_base64(img)
                        messages[0]["content"].append({
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}
                        })
                        
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=messages,
                        max_tokens=4096
                    )
                    return response.choices[0].message.content.strip()

            except Exception as e:
                error_msg = str(e)
                if attempt < max_retries and ("503" in error_msg or "429" in error_msg):
                    time.sleep(base_delay)
                    base_delay *= 2
                else:
                    console.print(Panel(f"[bold red]✖ API Error: {error_msg}[/bold red]", box=box.ROUNDED, border_style="red"))
                    return None
    return None

def capture_screenshot(html_file_path, output_image_path, quiet=False):
    if not quiet: console.print(f"[dim]Capturing DOM state for: {os.path.basename(html_file_path)}[/dim]")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1024,768")
    chrome_options.add_argument("--hide-scrollbars")
    try:
        driver = webdriver.Chrome(options=chrome_options)
        file_uri = f"file:///{os.path.abspath(html_file_path).replace(chr(92), '/')}"
        driver.get(file_uri)
        time.sleep(1)
        driver.save_screenshot(output_image_path)
        driver.quit()
        return True
    except Exception as e:
        console.print(Panel(f"[bold red]✖ Error capturing screenshot: {e}[/bold red]", box=box.ROUNDED, border_style="red"))
        return False

def clean_code_block(code_str):
    code_str = re.sub(r"^```(?:html|jsx|javascript)?\n", "", code_str, flags=re.IGNORECASE)
    code_str = re.sub(r"^```\n", "", code_str)
    code_str = re.sub(r"\n```$", "", code_str)
    return code_str

def evaluate_and_heal(screenshot_path, html_file_path, provider, ref_image=None, to_react=False, quiet=False):
    image_paths = [screenshot_path]
    prompt = "You are an elite UX Designer. The attached screenshot shows a broken/ugly HTML UI. "
    
    if ref_image and os.path.exists(ref_image):
        image_paths.append(ref_image)
        prompt += "The SECOND image is the target design mockup (the reference). Rewrite the CSS of the first image so it perfectly matches the aesthetics of the second image. "
    else:
        prompt += "Rewrite the HTML/CSS to fix the alignment, contrast, and layout. Make it a premium, dark-mode, glassmorphism design. "
        
    prompt += "Return ONLY the raw HTML code."
    
    healed_code = call_universal_llm_with_backoff(prompt, image_paths, provider, f"Executing Visual Healing via {provider.upper()}")
    
    if not healed_code: return False
    healed_code = clean_code_block(healed_code)
    
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.basename(html_file_path)
    name_part, _ = os.path.splitext(base_name)
    
    output_file = os.path.join(output_dir, f"{name_part}_healed.html")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(healed_code)
        
    if not quiet: console.print(Panel(f"[bold green]✔ SUCCESS. Healed UI deployed via {provider.upper()} to:[/bold green]\n[bold white]{output_file}[/bold white]", box=box.ROUNDED, border_style="green"))
    return True

def run_shell():
    print_welcome_header()
    active_provider = "google"
    screenshot_file = "current_ui.png"
    
    while True:
        try:
            user_input = Prompt.ask("\n[bold cyan]╭─[/bold cyan] [bold white]AutoHeal[/bold white] \n[bold cyan]╰─>[/bold cyan]").strip()
            if not user_input: continue
                
            parts = user_input.split(maxsplit=1)
            command = parts[0].lower()
            args = parts[1].strip() if len(parts) > 1 else ""
            if not command.startswith("/"): command = "/" + command
            
            if command in ["/exit", "/quit"]:
                console.print(Panel("[bold cyan]Session Terminated. Goodbye.[/bold cyan]", box=box.ROUNDED, border_style="cyan"))
                break
                
            elif command == "/help": print_help()
            elif command == "/clear":
                os.system('cls' if os.name == 'nt' else 'clear')
                print_welcome_header()
                
            elif command == "/status":
                status_text = f"Current Directory : [bold white]{os.getcwd()}[/bold white]\n"
                status_text += f"Active Brain Core : [bold magenta]{active_provider.upper()}[/bold magenta]"
                console.print(Panel(status_text, title="System Status", box=box.ROUNDED, border_style="cyan"))
                
            elif command == "/provider":
                if args.lower() in ["google", "openai", "opensource"]:
                    active_provider = args.lower()
                    console.print(Panel(f"[bold green]✔ AI Engine hot-swapped to: {active_provider.upper()}[/bold green]", box=box.ROUNDED, border_style="green"))
                else:
                    console.print(Panel("[bold red]✖ Invalid provider. Use: google, openai, or opensource[/bold red]", box=box.ROUNDED, border_style="red"))
                    
            elif command == "/heal":
                if args:
                    if capture_screenshot(args, screenshot_file):
                        evaluate_and_heal(screenshot_file, args, active_provider)
                        
            else:
                console.print(Panel("[bold red]✖ Unknown command. Type /help for available commands.[/bold red]", box=box.ROUNDED, border_style="red"))
                
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    run_shell()
