import sys
from dulwich import porcelain

repo_path = r'c:\Users\suhye\OneDrive\Desktop\review.ai'
repo = porcelain.open_repo(repo_path)

token = sys.argv[1].strip() if len(sys.argv) > 1 else None
if not token:
    try:
        import getpass
        token = getpass.getpass("GitHub Personal Access Token (ghp_...): ").strip()
    except Exception:
        token = input("GitHub Personal Access Token (ghp_...): ").strip()

if not token:
    print("Error: GitHub Token is required.")
    sys.exit(1)

auth_url = f"https://syw020110-yyyy:{token}@github.com/syw020110-yyyy/smartstore-review-curator.git"

try:
    print("Pushing to https://github.com/syw020110-yyyy/smartstore-review-curator.git (branch: main)...")
    porcelain.push(repo, auth_url, 'refs/heads/main:refs/heads/main')
    print("\n[SUCCESS] Successfully pushed to GitHub repository!")
    print("Check your repository at: https://github.com/syw020110-yyyy/smartstore-review-curator")
except Exception as e:
    print(f"\n[ERROR] Push failed: {e}")
    sys.exit(1)
