[< back to index](../doc_index.md)

## string

The `string` module automatically imports the [`err` module](./other.md).  

All the functions are designed to work for the strings in the default encoding.
If passed a string in an encoding that has a different null terminator,
then the results are undefined and the program will most likely crash or freeze.

#### `byte strzlen(pointer str)`

Calculates the length of a null-terminated string.  
If the string is longer than 255 bytes, then the behaviour is undefined (might even crash).

#### `sbyte strzcmp(pointer str1, pointer str2)`

Compares two null-terminated strings. Returns 0 if equal, non-0 if not equal.
If any of the strings is longer than 255 bytes, then the behaviour is undefined (might even crash).

#### `void strzcopy(pointer dest, pointer src)`

Copies the source null-terminated string into the destination buffer, including the string terminator.
If the source string is longer than 255 bytes, then the behaviour is undefined (might even crash).

#### `void strzpaste(pointer dest, pointer src)`

Copies the source null-terminated string into the destination buffer, excluding the string terminator.
If the source string is longer than 255 bytes, then the behaviour is undefined (might even crash).

#### `word strz2word(pointer str)`

Converts a null-terminated string to a number.
Sets `errno`.

#### `void strzappend(pointer buffer, pointer str)`
#### `void strzappendchar(pointer buffer, byte char)`

Modifies the given null-terminated buffer by appending a null-terminated string or a single character respectively.

## scrstring

The `scrstring` module automatically imports the `string` and [`err`](./other.md) modules.  

It contains functions for handling strings in the screen encoding with the same semantics as the functions from the string module.

#### `byte scrstrzlen(pointer str)`
#### `sbyte scrstrzcmp(pointer str1, pointer str2)`
#### `void scrstrzcopy(pointer dest, pointer src)`
#### `void scrstrzpaste(pointer dest, pointer src)`
#### `word scrstrz2word(pointer str)`
#### `void scrstrzappend(pointer buffer, pointer str)`
#### `void scrstrzappendchar(pointer buffer, byte char)`

## pstring

The `pstring` module automatically imports the [`err` module](./other.md).

It contains functions for handling length-prefixed strings in any 8-bit encoding.

#### `byte pstrlen(pointer str)`
#### `sbyte pstrcmp(pointer str1, pointer str2)`
#### `void pstrcopy(pointer dest, pointer src)`
#### `void pstrpaste(pointer dest, pointer src)`
#### `void pstrappend(pointer buffer, pointer str)`
#### `void pstrappendchar(pointer buffer, byte char)`
#### `word pstr2word(pointer str)`

Converts a length-prefixed string to a number. Uses the default encoding.
Sets `errno`.

#### `word pscrstr2word(pointer str)`

Converts a length-prefixed string to a number. Uses the screen encoding.
Sets `errno`.
