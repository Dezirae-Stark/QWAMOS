# QWAMOS Wiki Setup Instructions

The wiki pages have been created locally but need to be initialized on GitHub first.

## Method 1: Initialize Through GitHub Web UI (Recommended)

1. Go to: https://github.com/Dezirae-Stark/QWAMOS/wiki

2. Click **"Create the first page"** button

3. In the page editor:
   - Title: `Home`
   - Content: Copy from `Home.md` in this directory

4. Click **"Save Page"**

5. The wiki is now initialized! Continue with Method 2 to upload all pages.

## Method 2: Push All Wiki Pages via Git

Once the wiki is initialized (Method 1), you can push all pages:

```bash
cd /data/data/com.termux/files/home/QWAMOS.wiki

# Clone the now-initialized wiki
cd ..
git clone https://github.com/Dezirae-Stark/QWAMOS.wiki.git QWAMOS.wiki.live
cd QWAMOS.wiki.live

# Copy all pages
cp ../QWAMOS.wiki/*.md .

# Commit and push
git add *.md
git commit -m "docs: Add complete QWAMOS Wiki (8 pages)"
git push origin master
```

## Method 3: Manual Page Creation (if git push fails)

Create each page manually through the GitHub web UI:

1. Go to https://github.com/Dezirae-Stark/QWAMOS/wiki
2. Click **"New Page"**
3. For each `.md` file in this directory:
   - Copy the filename (without `.md`) as the page title
   - Copy the file content into the editor
   - Click **"Save Page"**

Pages to create:
- Home
- Overview
- Installation-&-Setup-Guide
- Architecture
- Security-Model
- Developer-Guide
- FAQ
- Roadmap

## Verification

After setup, verify all pages are accessible:

- https://github.com/Dezirae-Stark/QWAMOS/wiki/Home
- https://github.com/Dezirae-Stark/QWAMOS/wiki/Overview
- https://github.com/Dezirae-Stark/QWAMOS/wiki/Installation-&-Setup-Guide
- https://github.com/Dezirae-Stark/QWAMOS/wiki/Architecture
- https://github.com/Dezirae-Stark/QWAMOS/wiki/Security-Model
- https://github.com/Dezirae-Stark/QWAMOS/wiki/Developer-Guide
- https://github.com/Dezirae-Stark/QWAMOS/wiki/FAQ
- https://github.com/Dezirae-Stark/QWAMOS/wiki/Roadmap

## Wiki Content Summary

- **8 pages total**
- **4,262 lines of documentation**
- **100% internal linking between pages**
- **Professional Markdown formatting**
- **Code examples and ASCII diagrams**
- **Contact: qwamos@tutanota.com**
