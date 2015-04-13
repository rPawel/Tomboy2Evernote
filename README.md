# Tomboy2Evernote
Exports Tomboy Notes to Evernote Format

![Tomboy](docs/tomboy.png "Tomboy")

![Evernote](docs/evernote.png "Evernote")

# Usage
```bash
python Tomboy2Evernote.py -i ~/.local/share/tomboy -o ~/Desktop
```

# Info
## Tested with:
 - Python 2.7
 - Ubuntu 14.04
 
## Why this tool?
Although Tomboy has a great export to html functionality there are two issues with this
 - It fails sometimes: https://bugs.launchpad.net/ubuntu/+source/tomboy/+bug/983998
 - The exported html layout is not fully accepted by Evernote hence Tomboy's formatting looks broken there
