# Installation Guide for macOS

If you see a message saying **"'NPS Analysis.app' is damaged and can't be opened"** when trying to run the application, this is a standard macOS security feature for applications that are not signed with an Apple Developer Certificate.

To resolve this, please follow these steps:

1.  Move the **NPS Analysis.app** to your **Applications** folder.
2.  Open the **Terminal** app (Command + Space, type "Terminal").
3.  Copy and paste the following command and press Enter:

```bash
xattr -cr /Applications/"NPS Analysis.app"
```

4.  You should now be able to open the application normally.

## Why is this happening?
macOS automatically quarantines applications downloaded from the internet that are not notarized by Apple. The command above removes this quarantine attribute, allowing the app to run.
