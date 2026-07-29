# Git Initialization Guide

Follow these steps to initialize this project as a Git repository and push it to GitHub for the first time.

### 1. Initialize Git
Open your terminal in the root directory (`GreenRoute-V7`) and run:
```bash
git init
```
*This creates a hidden `.git` folder and makes this directory a local repository.*

### 2. Add Files to Staging
```bash
git add .
```
*This stages all files for the first commit, while respecting the rules in `.gitignore`.*

### 3. Create Initial Commit
```bash
git commit -m "Initial commit: GreenRoute V7 base project"
```
*This saves your files into the local repository's history.*

### 4. Create Main Branch
```bash
git branch -M main
```
*This ensures your primary branch is named `main`.*

### 5. Link to GitHub
Go to GitHub, create a new empty repository, and copy the repository URL. Then run:
```bash
git remote add origin <YOUR_GITHUB_REPOSITORY_URL>
```
*This links your local repository to the remote GitHub server.*

### 6. Push Code
```bash
git push -u origin main
```
*This uploads your code to GitHub. You are now ready to collaborate!*
