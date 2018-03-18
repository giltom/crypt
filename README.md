# crypt
What you are looking for is the python library in the directory `crypt`. The directories `scripts` and `ctf_solutions` include various scripts vaguely related to cryptography and most probably don't make sense. You shouldn't need them.

This runs on Python 3 and **requires** the `cryptography` library, which can be installed with pip.

You can simply type `from crypt import *` to get everything (except the `oracles`) module into the global namespace. Alternatively, you can import only some of the modules. The current modules are:

* `asymmetric` - asymmetric encryption
* `attacks` - generic implementations of some attacks.
* `byte` - a ton of convenient operations on bytes objects.
* `classic` - classical ciphers and modular operations on letters.
* `const` - Some constants. You probably don't need this.
* `encodings` - Convenient conversions between different data encodings/formats. No more need to remember the different functions to convert to/from hex, binary, base64, etc.
* `numbers` - Many number theory operations on integers. Make sure to use the functions isqrt and icbrt from here instead of x\*\*0.5, math.sqrt, etc.
* `oracles` - A few implementations of some simple oracles. Useful mostly for testing. Not imported into global namespace and you probably don't need it.
* `padders` - padding.
* `symmetric` - symmetric encryption.
* `util` - some utility functions.

Note that this is focused mostly on utility stuff for CTFs and not actually implementing the ciphers themselves. You can find functions for many ciphers in the `cryptography` library. Shorthands for some common ones can be found in `asymmetric` and `symmetric`.

There are too many functions to document them all here. All non-obvious functions have comments documenting them in the code. I'll just go over two common things:

## Encoding Conversions
The `encodings` module allows you to perform conversions easily without remembering different functions. All you need to do is call `convert(value, encfrom, encto)`, where encfrom and encto are the string names of the original encoding and the encoding to convert to respectively. The supported encodings are currently:

* `bytes` - normal Python bytes object.
* `hex` - hexadecimal string.
* `base64` - base64 string.
* `int_big` - int, big endian conversion.
* `int_little` - int, little endian conversion.
* `int` - same as `int_big`.
* `bin` - binary string.
* `bits` - list of integer bits (the ints 0 and 1).

You can also create an instance of Converter that performs conversion when called, by calling `Converter(encfrom, encto)`. This is more efficient for many conversions.

Finally, there are also functions like `hex2bytes(s)`, `bytes2bits(b)`, etc that perform direct conversions from and to bytes.

Here are some examples:

```
>>> convert('AAAA', 'hex', 'bin')
'1010101010101010'
>>> f = Converter('bytes', 'base64')
>>> f(b'abcd')
'YWJjZA=='
>>> hex2bytes('abcd')
b'\xab\xcd'
```

For operating on bytes, there are a ton of convenient functions in `byte`.

## Computation Time Limits
`util` provides a useful mechanism for limiting computation time using the context manager `time_limit(seconds)`. A `TimeoutException` is raised if the time runs out. For example:

```
with time_limit(timeout):
	try:
		do_something_hard()
	except TimeoutException:
		print('Timeout.')
```

Note that this uses `SIGALRM`, so it won't work on Windows, and you can't use `SIGALRM` for something else.
