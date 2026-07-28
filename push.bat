@echo off
echo Adding all changes...
git add .

echo Committing changes...
git commit -m "Organize project structure into tests/, scripts/, docs/reports/ and update README.md"

echo Pushing to branch role2-cupid-agent-complete...
git push origin role2-cupid-agent-complete

echo Push completed successfully!
pause
