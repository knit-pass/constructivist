# ---------------------------------------------------------------------------- #
#                                readability.py                                #
# ---------------------------------------------------------------------------- #

import textstat
from prettytable import PrettyTable


def get_rank(grade: float) -> int:
    """
    The function returns a rank based on a given grade, with special rankings for grades above a certain
    threshold.

    :param grade: a float representing readability grade of a given text
    :type grade: float
    :return: an integer value representing the rank of a given grade.
    """
    # Common: math.floor(grade / 4.5)
    # Special ranking
    if grade > 13:
        return 4
    elif grade >= 9:
        return 3
    elif grade >= 5:
        return 2
    else:
        return 1


def get_readability_report(sentence: str) -> None:
    """
    This function takes a sentence as input and generates a readability report that includes various
    readability indices such as Flesch-Kincaid Grade, Flesch-Kincaid Readability, Smog, and Gunning Fog
    Index.

    :param sentence: A string representing the sentence for which the readability report needs to be
    generated. The function uses the textstat library to calculate various readability metrics for the
    given sentence. The function also calls another function called get_rank to determine the grade
    level of the sentence based on the Flesch-Kincaid Grade
    :type sentence: str
    """
    x = PrettyTable()
    print("\n")
    print("Sentence: ", sentence)
    x.field_names = ["Index", "Value"]
    x.add_row(["Flesch-Kincaid Grade", textstat.flesch_kincaid_grade(sentence)])
    x.add_row(["Flesch-Kincaid Readability", textstat.flesch_reading_ease(sentence)])
    x.add_row(["Smog", textstat.smog_index(sentence)])
    x.add_row(["Gunning Fog Index,", textstat.gunning_fog(sentence)])
    x.align = "l"
    print(x)
    print("\n")
    print("\n")
    print("Rank: ", get_rank(textstat.flesch_kincaid_grade(sentence)))


def get_readability_rank(sentence: str) -> int:
    """
    The function takes a sentence as input and returns its readability rank using the Flesch-Kincaid
    grade formula.

    :param sentence: The input sentence for which we want to calculate the readability rank
    :type sentence: str
    :return: The function `get_readability_rank` takes a string `sentence` as input and returns an
    integer value which is the readability rank of the sentence calculated using the Flesch-Kincaid
    Grade formula from the `textstat` library.
    """
    return get_rank(textstat.flesch_kincaid_grade(sentence))
