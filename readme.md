Server protocol:
Syntax:
```
|   Message size (n)   |   Command   |            Arguments            |
|       2 bytes        |    1 byte   |          (n - 3) bytes          |
```

Commands:
* `0x01`: download resource at url


Example: download https://9p.io/plan9/img/plan9bunnywhite.jpg

```
00000000 00 2E 01 68 74 74 70 73 3A 2F 2F 39 70 2E 69 6F    ...https://9p.io
00000010 2F 70 6C 61 6E 39 2F 69 6D 67 2F 70 6C 61 6E 39    /plan9/img/plan9
00000020 62 75 6E 6E 79 77 68 69 74 65 2E 6A 70 67          bunnywhite.jpg
```