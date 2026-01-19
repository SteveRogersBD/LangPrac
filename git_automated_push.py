import subprocess
import sys

def run_command(command):
    try:
        # Run command and capture output
        result = subprocess.run(
            command, 
            check=True, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        if result.stdout:
            print(result.stdout.strip())
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(e.stderr)
        return False

def git_push():
    print("🚀 Starting Git Push Process...")
    
    # 1. Add all files
    print("\n📦 Adding files...")
    if not run_command("git add ."):
        return

    # 2. Get commit message
    while True:
        commit_message = input("\n📝 Enter commit message: ").strip()
        if commit_message:
            break
        print("Commit message cannot be empty!")

    # 3. Commit
    print("\n💾 Committing...")
    if not run_command(f'git commit -m "{commit_message}"'):
        return
    
    # 4. Push
    print("\n⬆️  Pushing to remote...")
    # -u origin HEAD pushes the current branch to a branch of the same name on origin
    # and sets it as upstream. Works for main, master, or any other branch name.
    if run_command("git push -u origin HEAD"):
        print("\n✅ content pushed successfully!")
    else:
        print("\n❌ Push failed.")

if __name__ == "__main__":
    git_push()
