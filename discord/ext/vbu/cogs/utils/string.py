import typing
import string


class PluralFormatter(string.Formatter):

    def format_field(self, value: typing.Any, spec: str) -> str:
        spec_split = spec.split(",")
        if spec_split[0] == "plural":
            _, single, multiple = spec_split
            if value == 1:
                return single
            return multiple
        return super().format_field(value, spec)


class PronounFormatter(string.Formatter):

    def format_field(self, value: typing.Any, spec: str) -> str:
        spec_split = spec.split(",")
        if spec_split[0] == "pronoun":
            _, personal, other = spec_split
            if value:
                return personal
            return other
        return super().format_field(value, spec)


class JoinFormatter(string.Formatter):

    def format_field(self, value: typing.Any, spec: str) -> str:
        spec_split = spec.split(",", 1)
        if spec_split[0] == "join":
            try:
                joiner = spec_split[1]
            except IndexError:
                joiner = ", "
            return joiner.join(value)
        elif spec_split[0] == "humanjoin":
            if len(value) == 1:
                return value[0]
            elif len(value) == 2:
                return " and ".join(value)
            else:
                return ", ".join(value[:-1]) + f", and {value[-1]}"
        return super().format_field(value, spec)


class ProgressFormatter(string.Formatter):

    # EMOJI_EMPTY = "<:ExpEmpty:879144403325812776>"
    # EMOJI_QUARTER = "<:ExpQuarter:879147649381568532>"
    # EMOJI_HALF = "<:ExpHalf:879144403321622539>"
    # EMOJI_THREE_QUARTERS = "<:ExpQuarter3:879147649364819999>"
    # EMOJI_FULL = "<:ExpFull:879144403325812777>"

    EMOJI_EMPTY = "\u258F"
    EMOJI_QUARTER = "\u258E"
    EMOJI_HALF = "\u258C"
    EMOJI_THREE_QUARTERS = "\u258A"
    EMOJI_FULL = "\u2588"

    def format_field(self, value: typing.Any, spec: str) -> str:
        spec_split = spec.split(",")
        if spec_split[0] == "progress":
            try:
                width = int(spec_split[1])
            except IndexError:
                width = 5
            section_values = 100 / width
            sections = []
            for i in range(width):
                if value >= section_values:
                    sections.append(self.EMOJI_FULL)
                elif value >= ((section_values * 3) / 4):
                    sections.append(self.EMOJI_THREE_QUARTERS)
                elif value >= (section_values / 2):
                    sections.append(self.EMOJI_HALF)
                elif value >= (section_values / 4):
                    sections.append(self.EMOJI_QUARTER)
                else:
                    sections.append(self.EMOJI_EMPTY)
                value -= section_values
            return "".join(sections)
        return super().format_field(value, spec)


class Formatter(PluralFormatter, PronounFormatter, JoinFormatter, ProgressFormatter):

    def format(self, *args, **kwargs):
        """
        A modified version of the normal :code:`str.format` method to have some slightly more
        useful utilities in it.

        Examples:

            ::

                # Saying how many of a given item you have can be a pain.
                # Using the plural formatter, you can easily format a string to have
                # plural nouns.
                vbu.format("{0:plural,single,plural}", 1)  # "single"
                vbu.format("{0:plural,single,plural}", 2)  # "plural"
                vbu.format("{0} {0:plural,item,items}", 1)  # "1 item"
                vbu.format("{0} {0:plural,item,items}", 2)  # "2 items"

                # You have a command `inventory` - runnable as `inventory @user` defaulting the user
                # to yourself.
                # Pronouns for this can be a pain to update in strings. In this example, we set the
                # pronouns by comparing the specified user to `ctx.author`
                vbu.format("{0:pronoun,You,{1.mention}} {0:pronoun,have,has} stuff.", ctx.author == user, user.mention)

                # The join formatter can "human" join a list strings.
                items = ["a", "b", "c", "d"]
                vbu.format("{0:humanjoin}", items)  # "a, b, c, and d"
        """

        return super().format(*args, **kwargs)
