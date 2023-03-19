# unzippy

`busybox unzip` wouldn't open one of my files, so I made this script with a
similar API, and it ***WORKED*** 💥🤾.

## install

```sh
python -m pip install unzippy
```

<details><summary>or with curl</summary><p>

```sh
curl -o ~/.local/bin/unzippy https://git.sr.ht/~rasch/unzippy/blob/main/unzippy.py
chmod +x ~/.local/bin/unzippy
```

</p></details>

## usage

```sh
# print help menu
unzippy -h

# extract files
unzippy archive.zip
```
