## <span style="color:#ff5555;">URO</span>

This language is an attempt to make the types concept more managable for beginners.
I plan to expand the language in that direction.
Below is all working code:


```uro
##
Here is an example with comments.
##

_read bits # This macro makes a 32-bit integer named bits

bits = bits + 4 # Minus, divide, and multiply also exist

_byte bits # Casts the integer to a byte type

bits = bits & 101by # by signifies byte type
bits = bits || 11by # This unlike most languages is actually a signed bitwise or operation
bits = bits | 10by # Then this is actually a signed bitwise xor operation
bits = !bits # Bitwise not operation
bits = bits < 1by # This is a shift left
bits = bits > 1by # This is a shift right

_int bits # Cast back to an integer to print

print(bits)

_write bits # Write to stdout

```

Dynamic variables do not fully work yet so use the keyword iflex.
If statements work but there are no elif or else as of this release.

```uro
iflex x = 40
x = x * x

if (x == 1600): # Use pythonic indentation
    print(x)
```

How to install:

The program scans by checking neighboring files and their children recursivly so put it wherever you like just keep that in mind.
Then once you have found a location go into project -> setups -> compiled and just run whichever version.
The Nim code is also available in project -> setups -> nim if you want to check my code.
I recommend the name URO for the project name. Btw it will not automatically update so you will have to download future versions off github.

How to use:

After you restart (what depends on os) you should be able to run the command: uro comp -a
Then find the binary in the folder local-cache.

Devs:

I did not know what to name this language for a long time while developing this project so you may find some names like rt or something in the source code.
Also "word" has not been updated to byte in the source code. 
Feel free to contribute ideas to the docs folder and I might add them to my personal docs folder.
I will consider pull requests but just know they are unlikely to make it because I have most plans layed out in my personal docs folder.
