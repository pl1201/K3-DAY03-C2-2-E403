@echo off
echo Adding all changes...
git add .

echo Committing changes...
git commit -m "Clean up root directory: moved all extra .md files to docs/reports/"

echo Pushing to branch role2-cupid-agent-complete...
git push pl1201 role2-cupid-agent-complete

echo Push completed successfully!
pause

