---
description: Deploy and release a new version of the NPS Analysis app
---

1. Check and bump the version in `frontend/package.json` if needed.
2. Build the backend:
   ```bash
   cd backend
   ./build_backend.sh
   cd ..
   ```
3. Build the frontend and package the Electron app:
   ```bash
   cd frontend
   npm run electron:build
   cd ..
   ```
4. Verify the build artifact (DMG) exists in `frontend/dist_electron/`.
5. Commit and push changes to the remote repository:
   ```bash
   git add .
   git commit -m "chore: bump version to <VERSION>"
   git push origin main
   ```
6. Create a GitHub release and upload the asset:
   ```bash
   gh release create v<VERSION> "frontend/dist_electron/NPS Analysis-<VERSION>-arm64.dmg" --title "v<VERSION>" --notes "Release notes here"
   ```
