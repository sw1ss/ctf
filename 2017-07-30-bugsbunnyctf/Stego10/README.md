# Stego10
Author: MH

This was the easiest steganography challenge - almost too easy to make a writeup
## Challenge description
```text
My comment :
Do you even need a description for this one ?!!
```
And the image:
![Stego 10](h4cker.jpg)

## Solution
The flag is in the comment of the image.
```bash
$ exiftool h4cker.jpg

ExifTool Version Number         : 10.58
File Name                       : h4cker.jpg
Directory                       : .
File Size                       : 32 kB
File Modification Date/Time     : 2017:07:29 21:03:38+02:00
File Access Date/Time           : 2017:07:29 21:03:38+02:00
File Inode Change Date/Time     : 2017:07:29 21:04:13+02:00
File Permissions                : rw-r--r--
File Type                       : JPEG
File Type Extension             : jpg
MIME Type                       : image/jpeg
JFIF Version                    : 1.01
Resolution Unit                 : inches
X Resolution                    : 96
Y Resolution                    : 96
Exif Byte Order                 : Little-endian (Intel, II)
Software                        : Google
Exif Version                    : 0220
Exif Image Width                : 700
Exif Image Height               : 300
Comment                         : Bugs_Bunny{0258c4a75fc36076b41d02df8074372b}
Image Width                     : 700
Image Height                    : 300
Encoding Process                : Baseline DCT, Huffman coding
Bits Per Sample                 : 8
Color Components                : 3
Y Cb Cr Sub Sampling            : YCbCr4:4:4 (1 1)
Image Size                      : 700x300
Megapixels                      : 0.210
```
