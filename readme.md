Server protocol:
Syntax:
```
|   Message size (n)   |   Command   |             Arguments           |
|       2 bytes        |    1 byte   |          (n - 3) bytes          |
```

Commands:
* `x01`: download resource at url


Example: download https://9p.io/plan9/img/plan9bunnywhite.jpg

```
00000000 01 68 74 74 70 73 3A 2F 2F 39 70 2E 69 6F 2F 70    .https://9p.io/p
00000010 6C 61 6E 39 2F 69 6D 67 2F 70 6C 61 6E 39 62 75    lan9/img/plan9bu
00000020 6E 6E 79 77 68 69 74 65 2E 6A 70 67 00 00 00 00    nnywhite.jpg
```