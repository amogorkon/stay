# STAY - Simple, even Trivial Alternative to Yaml

YAML may be readable by humans, but there are shortcomings. There is strict YAML, TOML etc. but they all suffer from the same false premise. If you have stuff hand-written by humans, you must validate one way or another. With pydantic a simple, yet powerful framework exists to validate and convert values into the desired format when the content is read. This means there simply is no point in type-hinting within the document, which adds ambiguity, unnecessary complexity and visual clutter, not to mention the annoying manual escaping of special characters that does nothing for usability.

STAY removes all that overhead and reduces syntax to the bare minimum, which can easily be parsed into pydantic to get what you want.

## Syntax
STAY is line-based. The file is read line by line, translated into a generator/list of dictionaries. 

### Documents
Dictionaries (aka documents) are seperated by lines that start with **===** or **---**. For instance, in a configuration this allows defaults on top of the file, user-defined values below, which overwrite the default.

### Simple values
From there simple key/value pairs are written like **key: value** on a single line. Leading and trailing whitespace is stripped. Anything that can be directly converted like int, str, float etc. doesn't require extra characters.

### Simple list
A simple list of values is written as **key: \[1 2 3 asdf "foo bar"\]**.

### Comments
Comments are also line-based. Any line that starts with # is ignored. Additionally, a block can be commented out by putting ### above and below of the block.

### Long values
Anything that involves linebreak (\n) characters would need to be manually escaped, but there is a simple solution to that: long values. A key: with **:::** instead of : will start a block of long value, where everything is escaped until a single line starting with triple colons (if inside the block, it can be manually escaped by \\:::, which is the only exception, everything else is parsed as-is).
 
    key:::
    long
    value
    :::
 
### Long lists
Similarly, you can make a list of strings where each line is an item (spaces, newlines and tabs at beginning and end are removed!):

	key:::[
	a
	b
	c
	]:::
However, unlike long values, long lists also work with the list syntax, so you can easily write a matrix like this:

	matrix:::[
	[1 2 3]
	[4 5 6]
	[7 8 9]
	]:::

### Hierachy
As with JSON or YAML, a single document/dictionary may be nested. Levels are indicated by indentation of tabs or spaces (4 is default).
    
    a:
        b:
            c:3
        foo: 4
    bar: 6
    
Long values can be used at any point, which ignore the indentation level until end of the block.

### Directives
In future, directives - lines starting with ***%*** outside of blocks - can be used to easily extend STAY without interfering with the rest of the syntax, for instance for third party modules, but right now there is no functionality associated.

### Known Limitations
STAY tries to be simple and *stay* simple, so there are limitations to the syntax that are not easily fixed without blowing the specs out of proportion.
For instance at this moment it isn't possible to easily implement dictionaries within lists (you could work around that with key-value pairs, but that might be cumbersome),
also a deeper nesting than lists-in-lists (long list/matrix syntax) is not supported at this moment.
Feel free to submit ideas on how to lift these limitations by means of syntax (if it doesn't add complexity!) or via directives.

## Use
You can load(file) or loads(line-iterator) to read stuff and dumps(dict-iterator) to convert stuff.
Examples can be found in the Showcase Jupyter Notebook (in /docs) or look at the tests.
Please keep in mind that STAY outputs a list of dictionaries with no check whatsoever for duplicate keys. 
If this is a problem for you, please consider writing a directive and submit a pull request.

***That's it - enjoy!***


