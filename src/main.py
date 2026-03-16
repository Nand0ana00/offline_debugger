import os
import sys
import asyncio
import subprocess
from pathlib import Path

# Add the project root to the system path to find 'backend'
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# Import core components from backend
from backend.scanner import CodeScanner
from backend.rag_engine import LocalRAGEngine
from backend.agents import DebuggingAgents
from backend.config import MODEL_PATH, logger

def run_target_code(file_path: Path) -> str | None:
    """
    Runs the target file and captures the actual error message.
    """
    try:
        # Use sys.executable to ensure we use the same Python environment
        result = subprocess.run(
            [sys.executable, str(file_path)],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(file_path.parent)
        )
        if result.returncode == 0:
            return None
        
        # Robustly extract error details from stderr
        stderr = (result.stderr or result.stdout or "").strip()
        if not stderr:
            return f"RuntimeError: Process exited with code {result.returncode}"
            
        lines = stderr.splitlines()
        # Find the last significant line (usually the exception type: message)
        for line in reversed(lines):
            if line.strip():
                return line.strip()
        return f"RuntimeError: {stderr[:100]}"
    except subprocess.TimeoutExpired:
        return "TimeoutError: Script execution timed out."
    except Exception as e:
        return f"SystemError: {e}"

async def run_tech_voyagers(target_file_path: str):
    """
    High-level orchestration for the command-line debugging pipeline.
    """
    print("\n" + "="*60)
    print("🚀 TECHVOYAGERS: DYNAMIC OFFLINE DEBUGGER (CLI v2.0)")
    print("="*60)

    target_path = Path(target_file_path).resolve()
    if not target_path.exists():
        print(f"❌ Error: File '{target_file_path}' not found.")
        return

    # --- STEP 0: DYNAMIC ERROR DETECTION ---
    print(f"📡 [STEP 0] Executing {target_path.name} to catch live errors...")
    error_msg = run_target_code(target_path)
    
    if not error_msg:
        print("✅ No errors detected! Your code is already working.")
        return

    print(f"⚠️  Caught Error: {error_msg}")

    # --- STEP 1: SCANNER ---
    print(f"🔍 [STEP 1] Scanning project context...")
    scanner = CodeScanner(str(PROJECT_ROOT))
    code_context = scanner.get_context_for_file(str(target_path))
    if "Error reading file" in code_context:
        print(f"❌ {code_context}")
        return

    # --- STEP 2: RAG ENGINE ---
    print(f"📚 [STEP 2] Querying local knowledge base...")
    rag = LocalRAGEngine(data_dir="knowledge_base")
    local_knowledge = rag.query_docs(error_msg)

    # --- STEP 3: MULTI-AGENT AI ORCHESTRATION ---
    print("🧠 [STEP 3] Initializing Offline AI Agents...")
    agents = DebuggingAgents(model_path=MODEL_PATH)
    
    if agents.llm is None:
        print("❌ AI Error: Model file missing or runtime failed to load.")
        return

    # Use the same consolidated pipeline as the Web API
    print("🤖 Analyzing bug, explanation, and fix safety...")
    pipeline_data = agents.multi_agent_pipeline(error_msg, code_context, local_knowledge)

    # --- FINAL REPORT OUTPUT ---
    print("\n" + "-"*60)
    print("🎯 FINAL DEBUGGING REPORT")
    print("-" * 60)
    print(f"🕵️  ANALYSIS: {pipeline_data.get('analysis', 'N/A')}")
    print(f"\n💡 EXPLANATION: {pipeline_data.get('explanation', 'N/A')}")
    print(f"\n✅ VERIFICATION: {pipeline_data.get('status', 'Verification unknown.')}")
    print("="*60 + "\n")

    # --- DYNAMIC AUTO-FIX (VIPER ORCHESTRATION) ---
    choice = input("�️  Would you like to generate an optimized fix using multi-agent research? (yes/no): ").strip().lower()

    if choice == 'yes':
        print("\n� Entering Viper Orchestration Mode (Researching context + Self-Critique)...")
        workspace_files = scanner.scan_workspace()
        
        # This triggered the full Research-Critic-Fix loop
        orchestration_result = await agents.viper_orchestration(error_msg, code_context, workspace_files)
        
        if orchestration_result.get("success"):
            fixed_code = orchestration_result["fix"]
            print(f"✨ {orchestration_result['path_taken']}")
            
            # Clean Markdown artifacts
            clean_code = fixed_code.replace("```python", "").replace("```", "").strip()

            print("\n" + "-"*60)
            print("📝 RECOMMENDED FIX:")
            print("-"*60)
            print(clean_code)
            print("-"*60)

            save_choice = input("\n💾 Save to file? (yes/no): ").strip().lower()
            if save_choice == 'yes':
                fixed_filename = f"fixed_{target_path.name}"
                fixed_path = target_path.parent / fixed_filename
                fixed_path.write_text(clean_code, encoding="utf-8")
                print(f"✅ Saved to '{fixed_filename}'.")
            else:
                print("� Save skipped.")
        else:
            print(f"⚠️  Fix generation failed validation: {orchestration_result.get('reason')}")
            if orchestration_result.get("fix"):
                print("\nProposed (but potentially flawed) fix:")
                print(orchestration_result["fix"])

    else:
        print("👋 Debugging complete. Good luck!")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "demo_bug.py"
    try:
        asyncio.run(run_tech_voyagers(target))
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as exc:
        print(f"\n❌ Unexpected CLI Failure: {exc}")
        logger.exception("CLI crash")
