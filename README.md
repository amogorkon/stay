# STAY - Simple, even Trivial Alternative to Yaml

## Purpose

### Background
There are several different types of communication: communication between humans, between humans and computers and between computers. The communication between machines can also be distinguished between one that is easily readable (but not writable) by humans and one that is not. In the area of communication between machines that is also readable by humans, there is no alternative to JSON - and if readability is of no concern, there is MessagePack, which is also an excellent choice.
For the communication between humans on the other hand, there is pseudo-code and all kinds of ad-hoc micro-language that - hopefully - is understood by the recipient.
Finally, there is the area of communication between humans and machines. In this area exist all kinds of languages that were designed for various purposes like configuration, all programming languages, specifications for mini-languages like regex or descriptive languages like html, latex, SQL and the like. The semantic web adds yet another aspect to this collection, with JSON-LD as possible solution. Here, it is not enough to simply put down data but it is also required to specify how this data must be interpreted - which necessitates more complex notation.

### Why STAY?
There already are several languages that address the area of communication between humans and machines for configuration, for instance YAML, TOML or INI. However, while YAML and the others may be readable by humans, they all suffer from various false premises.
One such premise is that "data should be self-documenting", meaning that it should be obvious if something is a string, number, truth value or somesuch. However, for a human reader there is very little point for this hint since the type normally is obvious merely by looking at the document. On the other hand, the program parsing the document MUST ALWAYS validate the data types - as only a simple typo could crash the program otherwise. So, no point in writing all those quotation marks, is there?
Another problem with various markup languages is that the basic language already allows too much, like unrestricted execution of statements within the parser by eval(). It should be the other way round: the basic language should do nothing but specify datastructures and provide a mechanism to specify behaviours. The receiving end then can decide how to handle the data as they see fit.

With pydantic there is a simple, yet powerful framework to validate and convert values into the desired format when the content is read. This means there simply is no point in implicite type-hinting within the document, adding unnecessary complexity and visual clutter, not to mention the annoying manual escaping of special characters that does nothing for usability.

STAY removes all the overhead and boils syntax down to the bare minimum, which can easily be parsed into pydantic or some other type converter/validator to get whatever data type is specified.

All of computer science revolves on an abstract level around three types of datastructures: lists, hashtables and graphs. It is STAYs objective to make it possible to mix and match these high-level datastructures without making simple things complicated. 

## Syntax
STAY is line-based. The file is read line by line, translated into a generator of dictionaries.

### Documents
A document represents a basic dictionary. Documents are the basic units that are yielded from the STAY parser. In text form, a document is seperated from the next by a line that starts with **===** or **---**. For instance, in a configuration this allows defaults on top of the file, user-defined values below, which overwrite the default. The seperator may also be used as a headline like **=== this is the next chapter**.

### Simple values
In a document, simple key/value pairs are written like **key: value** on a single line. Leading and trailing whitespace is stripped. If whitespace is meaningful around key or value, you can signify that with a ***"*** on either or both sides, directly adjacent of the ***:*** and its partner around the key/value.

    "  foo   ":"    bar     "

### Hierachy
As with JSON or YAML, dictionaries may be nested. Levels are indicated by indentation of tabs or spaces (4 is default).
    
    a:
        b:
            c:3
        foo: 4
    bar: 6
    
### Simple list
The arguments of a bash command is a simple list of arguments, which you can easily write as **key: \[1 2 3 asdf "foo bar"\]**.

### Comments
Comments are line-based. Any line that starts with # is ignored. Additionally, a block can be commented out by putting ### above and below of the block.

### Long values = text blocks
Anything that involves linebreak (\n) characters would need to be manually escaped, but there is a simple solution to that: long values. A key: with **:::** instead of : will start a block of long value, where everything is escaped until a single line starting with triple colons (if inside the block, it can be manually escaped by \\:::, which is the only exception, everything else is parsed as-is).
 
   key:::
long
value
:::

Within a block, you can ignore any outside indentation level. 
This is useful to store long text passages that can be copy&pasted with no modification. Please note that the end-block signifier also acts as comment, allowing to mirror the block header or add meta-data that may be used in a directive. Mirroring the block header hardly seems useful in a small example (which is why it isn't enforced by code), however if the block is very large it can be a big help since it is no problem to search for ":::key".
 
### List blocks
Similarly, you can make a list of strings where each line is an item (spaces, newlines and tabs at beginning and end are removed!):

	key:::[
	a
	b
	c
	]

However, unlike long values, long lists also work with the list syntax, so you can easily write a matrix like this:

	matrix:::[
	[1 2 3]
	[4 5 6]
	[7 8 9]
	]
    
### Graph blocks
In some cases, 
I took inspiration from the DOT language - in fact, graph blocks are valid DOT and can easily be parsed as such with a given directive.
This requires a directive because there are so many different ways  to represent the graph as a datastructure and many different libraries for this purpose.
On first glance there is no difference to pure text blocks, but with an active directive, graph blocks can easily be handled separately.

A graph block is signified with a ***:::{*** and ends with a ***}***. The end signifier allows the same annotation as all the other blocks, so that

    graph:::{
    a -> b -> c
    }:::graph
    
is valid syntax.

## Modifying behaviour
While all STAY documents MUST follow the language specification for interoperability, a document also can include statements that a parser MAY follow, but has no obligation to. In the contrary, it is advised to start with a bare parser and only add functionality that is required to properly handle a given document. Since it is possible to change all of the internal machinery of the parser and adding arbitrary functionality, there is a considerable risk of a security breach if unnecessary functionality is added and exploited in a document by an untrusted source. All additional functionality that modifies parser behaviour are called 'directives'.

### Commands
The simplest way to let the parser do additional work besides turning a source of strings into a datastructure (of strings) is by issuing simple line commands within the document.
This is done by the following syntax:

	% cmd args1 args2

which only has an effect if "cmd" has been passed into the parser as possible command, for instance like

	decode = Decoder(commands={"include": drv.include})

making the following a valid expression:

	% include include-test

inserting the content of the file "include-test" at the line currently being parsed.
Be aware that if the exact same line is part of the file being inserted, this will result in a recursion and possibly an infinite loop!
However, if include has not been passed into the Parser as valid command, only an error may be logged while the content of the file is still valid for parsers without the command. 
Multiple commands also can be concatenated (piped) with the results of the first passed into the next:

	% cmd1 args11 args12 % cmd2 args21 args 22

You also can redefine the functions the parser uses by replacing them in the cases dict, but the recommended way
for this (for instance for graph parsing) is to pass in a custom_cases dict into the Decoder class on init, which
overwrites the default cases for this instance.

### Directives
While commands only operate on single lines, it is possible to define **directives** (or environments or contexts, however you want to call them), which are functions the parser applies to everything it operates on beyond the activation. The simplest form of directive is a global one on a single line, after having passed in the function to the Decoder class:

	decode = Decoder(line_directives={"comments": lambda line: line.split("#")[0])})

which enables the user to activate the function within the document like so

	<comments>
	key: value # comment for this curious new value!

there is no need to deactivate the comment manually, but it simply can be done by:

	</comments>
	key: value # this is now part of the value again

Arguments can be given just like commands:

	<step func arg1 arg2>

It is important to note that the < > are mandatory to clearly identify the part of the document that belongs to the specification of the directive/environment.

	<replace
	a: b
	b: c
	>

which, if "replace" is defined accordingly, could instruct the parser to replace all "a"s with "b"s and so on, from this point on.

Depending on whether the function has been defined as valid line, key, value or struct directive, the function only gets access to this particular data.
If the same function is passed as key and value directive in the definition of the Parser, it would be called for both steps - key and value construction, replacing letters indiscrimantly.
However, if different functions were passed under the same "replace" tag to the Parser in the beginning as key and value directives, special cases for either keys or values can be handled more elegantly.

For instance, you can have only for keys or for values. For this, you start similar like above:

	decode = Decoder(key_directives={"comments": lambda s: s.split("#")[0]})

which is basically the same code, just "line_directive" replaced by "key_directive". Now you can have a document like so

	<comments>
	strange name for a key # explanation : value

And even both, key and value:

	decode = Decoder(key_directives={"comments": lambda s: s.split("#")[0]},
					value_directives={"comments": lambda s: s.split("#")[0]})

which allows the following:

	<comments>
	strange name for a key # explanation : strange value # explanation


### Meta-Directives
Finally, it is possible to check and alter directives and their arguments before they are executed.
This can be done for instance to ensure backwards-compatibility if changes were made to directives or to check for security issues before a directive is executed.

### Known Limitations
With the current implementation it isn't possible to make arbitrary lists of lists and lists of dicts/other structures. It is also not possible to use a list/tuple as key.


## First steps
First you need to build a decoder instance - functions to take care of special directives need to be passed in explicitely, which should be no issue to begin with. The instance can be called directly to 
	
	from stay import Decoder

	decode = Decoder()

	with open(somefilename) as file:
		list(decode(file))


You can decode(file, text or lines) to read stuff and encode(dict-iterator) to convert stuff into a STAY iterator of documents.
Examples can be found in the Showcase Jupyter Notebook (in /docs) or look at the tests.

***That's it - enjoy!***


