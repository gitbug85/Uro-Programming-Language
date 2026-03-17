## <span style="color:#ff5555;">URO</span>

Right now this language only has working 32-bit types.
It intends to simplify on the type system from most languages.


```uro
##
Here is an example with comments.
Note that unary operations do not currently exist but is planed.
##

_read bits # This macro makes a 32-bit integer named bits

bits = bits + 4 # Minus, divide, and multiply also exist

_byte bits # Casts the integer to a byte type

bits = bits & 101by # by signifies byte type
bits = bits || 11by # This unlike most languages is actually a signed bitwise or operation
bits = bits | 10by # Then this is actually a signed bitwise xor operation
bits = bits < 1by # This is a shift left
bits = bits > 1by # This is a shift right

_int bits # Cast back to an integer to print

print(bits)

_write bits # Write to stdout

```

How to install:

Right now only my Windows setup has been completed, so this language only works for Windows.
The program scans by checking neighboring files and their children recursivly so put it wherever you like just keep that in mind.
Then once you have found a location go into project -> setups -> compiled and just run the Windows version.
I recommend the name URO. Btw it will not automatically update so you will have to download future versions off github.

How to use:

After you restart you should be able to run the command: uro comp -a
Then find the binary in the folder local-cache.
