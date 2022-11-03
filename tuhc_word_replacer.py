import json
import string
from os.path import exists, abspath, expanduser, join
from os import walk
from random import randint
from re import search, compile, findall
from pyinputplus import inputFilepath, inputStr, inputYesNo
from tomllib import load as toml_load

"""
Title: Word replacer for the Unofficial Homestuck Collection.
Description: This is a program that, when run from the command line, creates a mod in js that can be used with TUHC. It
replaces any given string with any other string, accounting for typing quirks.
Authors: Amelia Pytosh, yabobay
Date Sept 18th, 2022
Version: b1.1.1
Depends: pyinputplus, Python 3.11+
"""

# Ultimate baller rev. 2 update: use an swf decompiler to get each individual
# image and line of text from it, and then replace the text as normal as below
# In addition, use cv2 to get the text from images and, rather than trying to
# figure out how to in-place replace the text, just generate a second file
# with a list of all swfs and images that contain the word that needs replacing.
# An exercise for the mod author!

"""
Version timeline goals:
1.1.1: Fish puns DONE!
1.1.2: Cat puns IN PROGRESS!
1.1.3: Horse puns IN PROGRESS!
1.1.4: Various misc puns (Maybe this can be where we account for feferi's ----------E thingy) IN PROGRESS!
1.2.0: Damara Google translate API bullshit NOT STARTED!
1.3.0: Homestuck 2 NOT STARTED!
2.0.0: Do the thing in the comment above ^^^ LOL NOT STARTED!

More todo ideas:
- Swearing system would be a system similar to fishpuns or catpuns where it would be a dict of words but maybe the vals
would be either a censored version of that word based on severity or just a severiry rating which the user could do with
as they please.
- Latula word replacer "Z" replacer would use a dict of nouns and a very low percent chance of accidentially tossing in
a "z" on the end of a word.
- Sollux and others change their quirk over the story. We can account for this by adding a little bit of code
to each of their sections to check the page number and if it after XYZ page number, use a different quirk.
Sollux: Alive -> Blind -> Half-dead
Caliborn: Callie alive -> Supreme
Aradia: Dead -> Alive
etc.
- Whispering characters could literally be determined with a dict of manually identified pages with whispering on it. 
Personally? No way in hell I'm doing that any time soon.
- All of the text converters or otherwise text-input-taking functions could be made into a standard form, either taking
whole strings of words or just single words.
- Shift away from global variables
- Replace the chumhandles and names dicts, along with all of the text-quirking code and all of the functions for
character-specific text modifications into a huge class that handles all of its stuff through a single object.
- Make all "error" variables into arguments and make their name more clear as to what their function is.

"""
# TODO TODO TODO TODO TODO
DEBUG = True
# TODO TODO TODO TODO TODO

FUN_MODE = True
# Set to false to disable all easter eggs.
# TODO: Add some various easter eggs, maybe False by default :(?


class Character():
    name = ""
    chumhandle = ""
    short_chumhandle = ""
    input_word_quirked = ""
    output_word_quirked = ""
    rules = {}

    def __str__(self):
        return self.name + " " + self.chumhandle + " " + self.input_word_quirked + " " + self.output_word_quirked + " " + str(self.rules)

    def __repr__(self):
        return self.name + " " + self.chumhandle + " " + self.input_word_quirked + " " + self.output_word_quirked + " " + str(self.rules)

    def __eq__(self, other):
        return self.name == other.name and self.chumhandle == other.chumhandle and self.input_word_quirked == other.input_word_quirked and self.output_word_quirked == other.output_word_quirked and self.rules == other.rules

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.name, self.chumhandle, self.input_word_quirked, self.output_word_quirked, self.rules))

    def set_name(self, name):
        self.name = inputStr("Enter the character's name: ") if not name else name

    def set_chumhandle(self, chumhandle):
        self.chumhandle = inputStr("Enter the character's chumhandle: ") if not chumhandle else chumhandle

    def set_input_word(self, input_word):
        input_word = inputStr("Enter the word you want to replace: ") if not input_word else input_word
        self.input_word_quirked = self._generate_quirk_word(self, input_word)

    def set_output_word(self, output_word):
        output_word = inputStr("Enter the word you want to replace it with: ") if not output_word else output_word
        self.output_word_quirked = self._generate_quirk_word(self, output_word)

    def set_rules(self, rules):
        self.rules = rules


    def _generate_quirked_word(self, word):
        rules = self.rules
        if rules == {}:
            return word
        else:
            for rule in rules:
                type = ""
                subtype = ""
                for rule_data in rules[rule]:
                    if rule_data == "type":
                        type = rules[rule]["type"].lower()
                    elif rule_data == "subtype":
                        subtype = rules[rule]["subtype"].lower()
                if type == "replacement":
                    if subtype == "regex":
                        pass
                        #TODO: Do this later lmao
                    elif subtype == "one-to-one":
                        word = word.replace(rules[rule]["start"], rules[rule]["end"])
                        # Potential TODO, change the syntax from "start" and "end" to "pattern" and "replacement"
                elif type == "case":
                    if subtype == "upper":
                        # UPPER
                        word = word.upper()
                    elif subtype == "lower":
                        # lower
                        word = word.lower()
                    elif subtype == "capitalize":
                        # Capitalize
                        word = word.capitalize()
                    elif subtype == "inverse":
                        # iNVERSE
                        # TODO: One of these two is wrong VVV
                        word = word.swapcase()
                    elif subtype == "alternating":
                        # aLtErNaTiNg
                        word = word.swapcase()
                    elif subtype == "alternating_words":
                        # alternating WORDS
                        pass
                        #TODO: Also do this one later
                elif type == "attachments":
                    if subtype == "prefix":
                        pass
                        # word = rules[rule]["prefix"] + word
                        # this is broken until I can make it work per-line rather than just for individual words
                    elif subtype == "suffix":
                        # word = word + rules[rule]["suffix"]
                        # same.
                        pass
                elif type == "puns":
                    if subtype == "substitution":
                        caps = True if word.isupper() else False
                        first = True if (word[0].isupper() if len(word) > 0 else False) else False
                        for pun in rules[rule]["puns"]:
                            if pun in word:
                                if word == pun:
                                    word = word.replace(pun, rules[rule]["puns"][pun])
                                    if caps:
                                        word = word.upper()
                                    elif first:
                                        word = word[0].upper() + word[1:]
                                    break
                                    # Breaking might be overkill!

                    elif subtype == "cursing":
                        pass
                        # DO this much later
                elif type == "none":
                    pass
                else:
                    print("ERROR: Rule type not recognized: ", self.name, type, subtype)
            return word

    def __init__(self, data, input_word, output_word):
        # Add the code here to parse whatever the TOML parser shits out
        self.name = data["name"].split(" ")[0].upper()
        self.chumhandle = data["handle"]
        self.short_chumhandle = data["handle_short"]
        data.pop("name")
        data.pop("handle")
        data.pop("handle_short")
        self.rules = data
        self.input_word_quirked = self._generate_quirked_word(input_word)
        self.output_word_quirked = self._generate_quirked_word(output_word)


def main() -> None:
    """
    This is the main body of the program.
    :return: Nothing :)
    """
    # TODO TODO TODO TODO TODO
    if DEBUG:
        debug_function()
    # TODO TODO TODO TODO TODO
    input_path, output_path = setup_filepaths()

    input_word = "fuck" if DEBUG else inputStr("Please enter the word you want to replace: ")
    output_word = "shit" if DEBUG else inputStr("Please enter the word you want to replace it with: ")

    characters = []
    for path, subdirs, files in walk("Characters"):
        for name in files:
            if len(join(path, name).split("\\")) < 3:
                # At this point you have a file object at join(path, name)
                # that is a character file or is in the appropriate folder
                # TOML interpretation code goes here TODO
                with open(join(path, name), "rb") as character_file:
                    character_data = toml_load(character_file)
                    characters.append(Character(character_data, input_word, output_word))
    # TODO: for each file in ./Characters/, create a character object and add it to the list/dict
    write_boilerplate(input_word, output_word, output_path, "header")

    # TODO: at this point we will need to go through the characters and generate the lines of modded text for every
    #   match. Good luck figuring that out, shitlips! Basically, re-create the original functionality with the new
    #  Character class.
    for character in characters:
        search_and_replace(input_path, output_path, input_word, output_word, character.input_word_quirked,
                           character.output_word_quirked, character.name,
                           character.short_chumhandle)

    write_boilerplate(input_word, output_word, output_path, "footer")

def search_and_replace(input_path: str, output_path: str, input_word: str,
                       output_word: str, input_quirked: list, output_quirked: list,
                       character_name: str, character_chumhandle: str) -> None:
    last_page_number = 000000
    with open(input_path, "r", encoding="utf-8") as open_file:
        # And here it begins, we start by reading the mspa.json file and parsing its contents.
        file_contents = open_file.read()
        # Taking the file and reading its contents as a single huge block
        json_contents = json.loads(file_contents)
        # Converting that block into a json formatted mega-structure. I will try and explain how this is structured
        # later, but it is honestly very confusing and often inconsistent. I think I have covered all my bases, but that
        # is what user testing is for, right?
        for story in json_contents:
            # "story" objects I *think* refers to the literal stories present on MSPA, be that JB, HS, whatever.
            # There are only a few of these, and they contain an absolutely unreal amount of "object_ids".
            for object_id in json_contents[story]:
                # I *would have* named this "page" but it seems to include some stuff that isn't a page. The key is a
                # page number, and the value is *usually* a dict full of shit, although there are a few lists for some
                # reason? TODO: look into that

                if type(json_contents[story]) == list:
                    pass

                elif type(json_contents[story]) == dict:
                    for item in json_contents[story][object_id]:
                        # An item is part of the dictionary value of an object, not every object has every value but
                        # all of them have titles, pageIds and content.
                        match item:
                            # All of these different items are extant for each page of the comic. We don't need
                            # most of them, but they're here just in case I wanted to do something with them in the
                            # future or if someone wanted to fork this program.
                            case "title":
                                # This is the title of the page, the text that appears at the top. This /can/ be
                                # different than the "next" text from the previous page, but it usually isn't.
                                pass

                            case "pageId":
                                # This is the page number of the page, in MSPA format.
                                if search(r"^\d\d\d\d\d\d$", json_contents[story][object_id][item]):
                                    # We make sure that, first, the page number is actually properly formatted
                                    # there are a few instances where it isn't a 6-digit number and those are indeed
                                    # ignored in this program, but it covers like 99.999% of all pages.
                                    if last_page_number != int(json_contents[story][object_id][item]):
                                        # Second, we make sure that the page number we are reading is not the same
                                        # page number as the last item we were working on. Now that I think about it,
                                        # I don't think this statement matters because if I didn't check it would just
                                        # be overwriting the same value, but whatever, it's here.
                                        last_page_number = int(json_contents[story][object_id][item])

                                else:
                                    last_page_number = 0
                            case "timestamp":
                                # This indicates the time in which the page was posted.
                                pass

                            case "flag":
                                # I have no idea what this is.
                                pass

                            case "media":
                                # This contains the link to the image/swf/mp4/whatever that exists on the page.
                                # Fun fact, this is the reason that every page of Homestuck is limited to a single
                                # piece of media. There are ways around this, but it is very, VERY hack-y
                                pass

                            case "content":
                                # Here's the good stuff, the page content, which is usually words exclusively.
                                for line_unstripped in json_contents[story][object_id][item].split("<br />"):
                                    line = format_input(strip_html(line_unstripped))
                                    # Go ahead and read the format_input() and strip_html() functions below to
                                    # figure out what this does, but in short words it basically converts the raw
                                    # line of text split from an entire page's content and cleans all the extra
                                    # formatting off of it, rendering it much easier to modify.

                                    # figure out the chum handle of the person speaking in this line
                                    try:
                                        pre_name = line[0:line.index(':')]
                                    except ValueError:  # the line doesn't a chum handle at all, so we have to set it to something i guess
                                        # This might break shit? Who knows
                                        pre_name = line[0:15]
                                    # if the chum handle matches a character with some sort of typing quirk
                                    if "".join(pre_name) in [character_chumhandle, "P"+character_chumhandle,
                                                             "C" + character_chumhandle, "F" + character_chumhandle] \
                                            and character_chumhandle != "N/A":
                                        # this converts that chum handle into a lowercase character name
                                        srch = compile(r"[^" + string.ascii_letters + r"1234567890]+" +
                                                       input_quirked.replace("(", "\(").replace(")","\)") +
                                                       r"[^" + string.ascii_letters + r"1234567890]+")
                                        # This compiles a regex for the input text. It breaks down as such:
                                        # [^ - Negated set, meaning "match any character not in this list"
                                        #   abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890 - The list.
                                        # ]+ - "+" identifies "1 or more" meaning "make sure there is at least one"
                                        # input_quirked[key] - This is the input word, converted into whatever
                                        #                      character's quirk that we are currently working on.
                                        # [^ - Same as the first one.
                                        #   abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890
                                        # ]+
                                        # All of this comes together to produce a regex that specifically looks for
                                        # the exact word that the user inputs. This helps avoid mis-identifications for
                                        # words that happen to be in other words. i.e. "playtest" has "test" in it.
                                        # It does this by making sure there is a non-alphanumeric character before and
                                        # after the word in question, be that a space, a "start-of-text" character, or
                                        # whatever else.
                                        if search(srch, line):
                                            # Now we search the line using the regex.
                                            extras = search(srch, line).group().split(input_quirked) \
                                                if input_quirked else ["", ""]
                                            # "extras" are the extra bits on the ends of identifications, be that
                                            # spaces, commas, whatever. This allows us to re-add them in after doing the
                                            # replacement.
                                            write_to_mod(line, line.replace(extras[0] + input_quirked + extras[1],
                                                                            extras[0] + output_quirked + extras[
                                                                                1]), last_page_number, output_path)
                                            # write_to_mod() writes the appropriate line of text to the mod file to
                                            # replace one word with another. You can see that we add the extras back on.

                                    elif "".join(pre_name) == character_name and character_name != "N/A":
                                        # This was removed for some reason? This is important for finding the chars who
                                        # do not have a chumhandle, but only a name. Otherwise it is just a duplicate of
                                        # the above code.
                                        for length in [6, 8, 12, 13]:
                                            if line[0:length] == character_name:
                                                srch = compile(r"[^" + string.ascii_letters + r"1234567890]+"
                                                               + input_quirked.replace("(", "\(").replace(")","\)") +
                                                               r"[^" + string.ascii_letters + r"1234567890]+")
                                                if search(srch, line):
                                                    extras = search(srch, line).group().split(input_quirked) \
                                                        if input_quirked else ["", ""]
                                                    write_to_mod(line, line.replace(extras[0] + input_quirked +
                                                                                    extras[1], extras[0] +
                                                                                    output_quirked + extras[1]),
                                                                last_page_number, output_path)
                                    elif character_name == "N/A" and character_chumhandle == "N/A":
                                        # And finally, everyone else. because there are no other typing quirks present
                                        # in other characters (besides roxy when she is drunk, I guess? Good luck
                                        # sorting that out lol), we can just pass it all to "other" which just replaces
                                        # the text without doing any substitutions.
                                        srch = compile(r"[^" + string.ascii_letters + r"1234567890]+" +
                                                       input_quirked.replace("(", "\(").replace(")", "\)") +
                                                       r"[^" + string.ascii_letters + r"1234567890]+")

                                        if search(srch, line):
                                            extras = search(srch, line).group().split(input_quirked) \
                                                if input_quirked else ["", ""]
                                            write_to_mod(line, line.replace(extras[0] + input_quirked + extras[1],
                                                        extras[0] + output_quirked + extras[1]), last_page_number,
                                                         output_path)
                            case "next":
                                # This indicates the title of the next page, i.e. the link at the bottom of the page.
                                pass

                            case "previous":
                                # This indicates the title of the previous page. i.e. the link at the very bottom of the
                                # page.
                                pass

                            case "theme":
                                # This indicates the page theme. Like homosuck, trickster mode, etc.
                                pass

                            case "scratchBanner":
                                # I have no idea what this is.
                                pass

def format_input(content: str) -> str:
    """
    This takes the raw escaped shit from the mspa.json and makes it actually not shit.
    I don't know what else to say, that's all there is to it.
    :param content: A string to remove all the html escaped shit from.
    :return: A string with all the html escaped shit removed from it.
    """

    return content.replace("\\\"", "\"").replace("\\n", "\n") \
        .replace("\\t", "\t").replace("\\\\", "\\").replace("</ br>", "</br>") \
        .replace("&gt;", ">").replace("&lt;", "<").replace("&quot;", "\"").replace("&amp;", "&")


def format_output(content: str) -> str:
    """
    This takes the final compiled string and re-formats it for js.
    I don't know what else to say, that's all there is to it.
    :param content: A string to replace all the improperly formatted js stuff.
    :return: A string with all the js stuff properly formatted.
    """

    return content.replace("\"", "\\\"").replace("\n", "\\\n").replace("\t", "\\t").replace("'", "\\\'")


def strip_html(content: str) -> str:
    """
    This takes in a string and returns it with all html tags removed.
    :param content: A string to remove all html tags from
    :return: A string without html tags
    """
    clean = compile(r"<[^<>]+>")
    for occurrence in findall(clean, content):
        # this accounts for multiple html tags in one string, which is basically a certainty.
        content = content.replace(occurrence, "")

    return content

def peixes_capital_e(content: str) -> str:
    """
    You know that thing where feferi gets -----EXIT-----ED and she does that thing with the ----E to make it look like
    a trident? This does that. This will NOT convert backwards, that is TODO!
    :param content: The string to be converted. Can be multiple words
    :return: The converted string.
    """
    if determine_excitedness(content) >= 0.8:
        # This is a very basic check to see if the string is excited enough to be converted.
        words = text.split(" ")
        caps_words_indexes = []
        for index, word in enumerate(words):
            if word.isUpper():
                caps_words_indexes.append(index)
        for index in caps_words_indexes:
            length = randint(5, 18) # These numbers are arbitrary, and may be changed in future versions!
            error = randint(0, 100)
            if error <= 70:
                # 70% chance of a capital E being converted into a trident
                words[index] = words[index].replace("E", "-"*length + "E")
    return " ".join(words)

def vriska_vowel_converter(content: str, construct: bool=True) -> str:
    """
    Converts a string into a Vriska vowel-extended version of itself. Takes a single word as input!
    :param content: A string containing a single word. This is the word to be converted.
    :param construct: Either makes the word vriska-y or un-vriskifies it. True for vriska-y, False for un-vriskifying.
    :return: The converted string.
    """
    if construct:
        # If a word is being converted into a vriska-y version of itself
        error = randint(0, 100)
        # "error" in the sense of "What is the percent chance that the speaker does not make an error".
        vowels = {}
        # This is a dictionary of all the vowels in the word, and their indexes.

        for index, letter in enumerate(content):
            if letter in "aeiou":
                # VOWELS!
                vowels[index] = letter
        match len(vowels):
            # Match how many vowels there are in the word
            case 0:
                # Do nothing
                return content
            case 1:
                # If there is only one, we can do a much faster version of this process
                if error <= 50:
                    for letter in content:
                        if letter in "aeiou":
                            return content.replace(letter, letter*8)
            case _:
                # If there is more than one, spin up the process to convert all of them
                # TODO: This breaks because when the vowels get extended they change the indexes of the other vowels
                easter_egg = 0
                while error <= 50 and len(vowels) > 1:
                    easter_egg += 1 if FUN_MODE else 0
                    selection = choice(list(vowels.keys()))
                    content = content.replace(vowels[selection], vowels[selection]*8)
                    del vowels[selection]
                    error = randint(0, 100)
                if easter_egg > 3:
                    # TODO: Add easter egg
                    # AMELIA: Wow, that's a lot of vowels!
                    pass
                return content
    else:
        # Convert it back into a normal word from a vriska-y word
        repeated_vowels = {}
        for index, letter in enumerate(content):
            if letter in "aeiou":
                if letter*8 in content:
                    # I don't really know what to say here in particular other than, "Man, I really am glad I am using
                    # python right now!".
                    repeated_vowels[index] = letter
        for index in repeated_vowels:
            content = content.replace(repeated_vowels[index]*8, repeated_vowels[index])
        return content

def determine_excitedness(content):
    """Determines how excited the speaker is.

    :param content: The string to be converted.
    :return: The converted string.
    """
    caps = 0
    characters = 0
    all = 0

    for letter in content:
        # For each character in the string, check if it is alphanumeric. If it is, add it to the total character count.
        if letter.isalpha():
            # For each of those, if it is uppercase, add it to the uppercase character count.
            if letter.isupper():
                caps+=1
            characters+=1
        all += 1
    # The percentage of uppercase characters is the excitedness of the speaker.
    return round(caps/characters, 2)


def write_to_mod(original: str, replace: str, page: int, output_path: str) -> None:
    """
    This code takes an input string, an output string and a page number, and uses that to build a single
    archive.mspa.story[].content.replace() line.
    :param original: The original text from the comic that is the target for replacement
    :param replace: The text to replace original with.
    :param page: The page number that this content is located on
    :return: Nothing :)
    """
    page = "0" * (6 - len(str(page))) + str(page)
    # Sometimes the page number doesn't have padded 0's, this converts it into the appropriate format and also makes it
    # into a string.
    original = format_output(original)
    replace = format_output(replace)

    with open(output_path, 'a', encoding="utf-8") as open_file:
        open_file.write("      archive.mspa.story['" + str(page) + "'].content = archive.mspa.story['" + str(page) +
                        "'].content.replace('" + original + "', '" + replace + "')\n")

def setup_filepaths() -> tuple:
    """
    This function sets up the filepaths for the input and output files.
    :return: A tuple containing the input and output filepaths.
    """
    output_valid = True if DEBUG else False
    input_path = "mspa.json" if DEBUG else ""
    output_path = "mod.js" if DEBUG else ""
    while not output_valid:
        input_path = inputFilepath("Please enter the filepath for your mspa.json file "
                                   "(Located in Asset Pack/archive/data/mspa.json: ")
        input_path = abspath(expanduser(input_path))
        if exists(input_path):
            output_valid = True
        else:
            print("File doesn't exist!")

    output_valid = True if DEBUG else False
    while not output_valid:
        output_path = inputFilepath("Please enter the filepath for your finished mod: ")
        output_path = abspath(expanduser(output_path))
        if exists(output_path):
            if inputYesNo(output_path + " exists, overwrite? ") != "no":
                output_valid = True
            else:
                output_valid = False
        else:
            output_valid = True
    return input_path, output_path

def write_boilerplate(input_word: str, output_word: str, output_path: str, position: str)-> None:
    """
    Writes the boilerplate code to the output file.
    :param output_path: The path to the output file.
    :return: Nothing :)
    """
    if position == "header":
        with open(output_path, "w", encoding="utf-8") as open_file:
            # Here we quickly write all the boilerplate code that lives at the top of any mod. Once the mod has been
            # generated, the author is able to edit whatever they want. Credit would be preferred, but I'm not your mom.
            # Go wild.
            boilerplate = ""
            boilerplate += "module.exports = {\n"
            boilerplate += "    title: \"Mod where \\\"" + input_word + \
                           "\\\" is replaced with \\\"" + output_word + "\\\"!\",\n"
            boilerplate += "    author: \"Amelia P. " \
                           "(<a href='https://github.com/fourteevee/tuhc-word-replacer'>GitHub</a>\",\n"
            boilerplate += "    modVersion: 2.0,\n"
            boilerplate += "    description: `<h3>File auto-generated by the TUHC word replacer. All instances of \\\"" \
                           + input_word + "\\\" replaced with \\\"" + output_word + "\\\".</h3>`,\n"
            boilerplate += "    trees: {\n"
            boilerplate += "        './advimgs/': 'assets://advimgs/',\n"
            boilerplate += "        './storyfiles/': 'assets://storyfiles/',\n"
            boilerplate += "        './sweetbroandhellajeff/': 'assets://sweetbroandhellajeff/',\n"
            boilerplate += "        './archive/comics/': 'assets://archive/comics/'\n"
            boilerplate += "    },\n"
            boilerplate += "\n"
            boilerplate += "    edit(archive {\n"
            open_file.write(boilerplate)
    elif position == "footer":
        with open(output_path, "a") as open_file:
            open_file.write("    },\n")
            open_file.write("}")
        # Finally, we write the boilerplate footer code and call it a day!
def debug_function():
    pass
    #exit(0)

if __name__ == "__main__":
    main()
