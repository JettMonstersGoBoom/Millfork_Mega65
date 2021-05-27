[< back to index](../doc_index.md)

# Preprocessor

The Millfork preprocessor does 2 things:

* filters lines in the input file according to current target's features

* injects the target's feature values as constants into the current file

Despite its similarity to the C preprocessor, it's much more restricted in its power:

* no file inclusion

* no macros 

* separate namespaces for the preprocessor and the language (you need to use `#use` to use a preprocessor constant in the code)

Preprocessor directives by default start with `#`.
To avoid conflicts with C preprocessor (for users wishing to use it), it is also possible to replace `#` with `$$`.

### Defining feature values

Feature values are defined in the `[define]` section of the platform definition file.  
Each value is a signed 64-bit integer number.

Example:

    [define]
    WIDESCREEN=1
    
You can also define feature values using the `-D` command line option.

### Built-in features

The following features are defined based on the chosen CPU and compilation options:

* `MILLFORK_VERSION` – defined since 0.3.4, contains the version of the compiler: for version x.y.z, the value is 10000x+100y+z

* `ARCH_6502` – 1 if compiling for 6502, 0 otherwise

* `ARCH_I80` – 1 if compiling for Intel 8080-like processor, 0 otherwise

* `ARCH_X86` – 1 if compiling for Intel 8086-like processor, 0 otherwise

* `CPU_65C02`, `CPU_65CE02`, `CPU_65816`, `CPU_HUC6280`, `CPU_8080`, `CPU_8085`, `CPU_GAMEBOY`, `CPU_Z80`, `CPU_8086`
– 1 if compiling for the exact given processor, 0 otherwise

* `CPU_6502` – 1 if compiling for any pre-65C02 6502-like processor, 0 otherwise

* `CPUFEATURE_DECIMAL_MODE` – 1 if decimal mode is enabled, 0 otherwise

* `CPUFEATURE_65C02`, `CPUFEATURE_65CE02`, `CPUFEATURE_HUC6280`, `CPUFEATURE_65816_EMULATION`, `CPUFEATURE_65816_NATIVE`,
`CPUFEATURE_8080`, `CPUFEATURE_8085`, `CPUFEATURE_GAMEBOY`, `CPUFEATURE_Z80`,
`CPUFEATURE_6502_ILLEGALS`, `CPUFEATURE_8085_ILLEGALS`, `CPUFEATURE_Z80_ILLEGALS`, `CPUFEATURE_Z80_NEXT` – 1 if given instruction subset is enabled, 0 otherwise

* `ENCCONV_SUPPORTED` - 1 if the module `encconv` supports the function `to_screencode` and other related functions, 0 otherwise.

* `ENCODING_SAME` - 1 if the encodings `default` and `src` are the same, 0 otherwise.

* `ENCODING_NOLOWER` – 1 if the `default` encoding does not support lowercase ASCII letters.

* `DECIMALS_SAME` - 1 if the encodings `default` and `src` have the same string terminator and decimal digits `'0'`-`'9'`, 0 otherwise.

* `NULLCHAR_SAME` - 1 if the encodings `default` and `src` have the same string terminator, 0 otherwise.

* `NULLCHAR` – the value of the `nullchar` constant

* `NULLCHAR_SRC` – the value of the `nullchar_src` constant

* `INIT_RW_MEMORY` – 1 if the option `ram_init_segment` is defined, 0 otherwise.
See [the ROM vs RAM guide](../api/rom-vs-ram.md) for more information.

* `BIG_ENDIAN` – 1 if the platform is big-endian, 0 otherwise (currently all supported platforms are little-endian)

* `LITTLE_ENDIAN` – 1 if the platform is little-endian, 0 otherwise (currently all supported platforms are little-endian)

* `OPTIMIZE_FOR_SIZE`, `OPTIMIZE_FOR_SPEED`, `OPTIMIZE_INLINE`, `OPTIMIZE_IPO`
– 1 if given optimization setting is enabled, 0 otherwise

* `SYNTAX_INTEL`, `SYNTAX_ZILOG` – 1 if given assembly syntax is chosen, 0 otherwise; doesn't take this file's pragmas into account

* `USES_ZPREG` – 1 if the zeropage pseudoregister is used, 0 otherwise

* `ZPREG_SIZE` – size of the pseudoregister in bytes, or 0 on platforms that don't use it

* `TINY_RW_MEMORY` – 1 if the main ram is 256 bytes or less, 0 otherwise

* `USES_IX_STACK`, `USES_IY_STACK` – 1 if given index register is used as a base pointer for stack-allocated variables, 0 otherwise 

* `USES_SHADOW_REGISTERS` – 1 if interrupts preserve old registers in the shadow registers, 0 if they do it on stack

* `USES_SOFTWARE_STACK` – 1 if using software stack for variables (6502-like targets only), 0 otherwise

### Commonly used features

These features are frequently defined in the platform definition file.
Some libraries may require that some of these be defined.

* `WIDESCREEN` – 1 if the horizontal screen resolution, ignoring borders, is greater than 256, 0 otherwise

* `TALLSCREEN` – 1 if the vertical screen resolution, ignoring borders, is greater than 256, 0 otherwise

* `KEYBOARD` – 1 if the target has a keyboard, 0 otherwise

* `USE_MOUSE_MBM` –  set this to 1 if you want to enable middle button support for the mouse. 

* `JOYSTICKS` – the maximum number of joysticks using standard hardware configurations, may be 0

* `HAS_BITMAP_MODE` – 1 if the target has a display mode with every pixel addressable, 0 otherwise

* `NTSC` – 1 if the target is NTSC, 0 otherwise

* `PAL` – 1 if the target is PAL, 0 otherwise

* `NULLPTR` – physical value of `nullptr`, default 0

### Target-specific features

These features are used to identify the target machine in multiplatform programs and libraries:

* `CBM` – 1 if the target is an 8-bit Commodore computer (or a compatible one), 0 otherwise
(for more Commodore-related preprocessor options, see [Preprocessor options for Commodore computer targets](./preprocessor_cbm.md))

* `AMSTRAD_CPC`, `ATARI_2600`, `ATARI_8`, `ATARI_LYNX`, `APPLE_2`, `BBC_MICRO`,
`COMMANDER_X16`, `CPM`, `GAMEBOY`, `IBM_PC`, `MSX`, `NEC_PC_88`, `NES`, `ZX_SPECTRUM`
– 1 if the target is the machine in question, 0 otherwise

* `VERA_VERSION` – on Commander X16, the version of the VERA chip: `7` for 0.7, `8` for 0.8, `9` for 0.9


### Built-in preprocessor functions and operators

The `same` function returns 1 if given identical identifiers and 0 otherwise.
It is the only function that does not support any other kind of parameters, and it's only useful in module templates.

    // prints 1:
    #infoeval same(a,a)
    // prints 0:
    #infoeval same(a,b)
    // fails to compile
    #infoeval same(a,1)

The `defined` function returns 1 if the feature is defined, 0 otherwise.  
All the other functions and operators treat undefined features as if they were defined as 0. 

The `if` function returns its second parameter if the first parameter is defined and non-zero, and the third parameter otherwise:

    // prints 400:
    #infoeval if(1, 400, 500)
    // prints 500:
    #infoeval if(0, 400, 500)

The `min` and `max` functions return the smallest or largest parameter respectively. They support any number of arguments:

    // prints 400:
    #infoeval min(400, 500, 600)
    // prints 500:
    #infoeval max(400, 500)

The following Millfork operators and functions are also available in the preprocessor:  
`not`, `lo`, `hi`, `+`, `-`, `*`, `|`, `&`, `^`, `||`, `&&`, `<<`, `>>`,`==`, `!=`, `>`, `>=`, `<`, `<=`

The following Millfork operators and functions are not available in the preprocessor:  
`$+`, `$-`, `$*`, `$<<`, `$>>`, `:`, `>>>>`, `nonet`, all the assignment operators


### Character literals

Preprocessor supports character literals. By default, they are interpreted in the default encoding,
but you can suffix them with other encodings.

    // usually prints 97:
    #infoeval 'a'
    // prints 97:
    #infoeval 'a'ascii

Exceptionally, you can suffix the character literal with `utf32`.
This gives the literal the value of the Unicode codepoint of the character:

    // may print 94, 96, 112, 173, 176, 184, 185, 222, 227, 234, 240, something else, or even fail to compile:
    #infoeval 'π'
    // prints 960:
    #infoeval 'π'utf32

Escape sequences are supported, as per encoding. `utf32` pseudoencoding supports the same escape sequences as `utf8`.


### `#template`

Defines the source to be a module template. See [Modules](./modules.md) for more information.


### `#if/#elseif/#else/#endif`

    #if <expr>
    #elseif <expr>
    #else
    #endif

TODO

### `#fatal/#error/#warn/#info`

    #fatal fatal error message
    #error error message
    #warn warning message
    #info informational message
    
Emits a diagnostic message.

`#fatal` interrupts the compilation immediately.  
`#error` causes an error, but the compilation will continue.  
`#warn` emits a warning. It may be treated as an error depending on compilation options.  
`#info` emits a benign diagnostic message.

### `#infoeval`

    #infoeval <expr>
    
Evaluates an expression and emits the result as a diagnostic message.

### `#define`

    #define <ident> = <expr>

Defines a new feature value or redefines a previous feature value.

The feature value is visible only to the preprocessor, only when processing the current file,
and only in lines preprocessed after this one. 

### `#use`

    #use <ident> = <expr>
    
    #use <feature>
    // equivalent to #use <feature> = <feature>

Exports a value to the parser.
The parser will substitute every use of the given identifier as a variable or constant 
with the numeric value of the feature.

    #use CPU_MODEL = if(CPU_65816 | ARCH_X86, 16, 8)
    putstrz("Your CPU is "z)
    putword(CPU_MODEL)
    putstrz("-bit."z)

The substitution will happen only within the current file.
To use such value in other files, consider using a normal constant:

    #use WIDESCREEN
    const byte is_widescreen = WIDESCREEN
    
### `#pragma`

Changes the behaviour of the parser for the current file.
The change applies to the whole file, regardless of where the directive is located. 

 * `#pragma intel_syntax` – interpret assembly using Intel syntax
 
 * `#pragma zilog_syntax` – interpret assembly using Zilog syntax

