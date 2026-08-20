import sys
import json
from pathlib import Path

# Adjust system path to support absolute imports for backend modules
workspace_root = Path(__file__).resolve().parent.parent
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

from backend.app.pipeline import analyze_resume

def main():
    if len(sys.argv) < 3:
        print("Error: Missing arguments.", file=sys.stderr)
        print("Usage: python main.py <resume_path> \"<job_description>\"", file=sys.stderr)
        sys.exit(1)

    resume_path = sys.argv[1]
    job_description = sys.argv[2]

    try:
        result = analyze_resume(resume_path, job_description)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
