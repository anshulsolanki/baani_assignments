import nltk
from nltk.corpus import framenet15 as fn

from exercise_3_1 import exercise_3_1
from exercise_3_2 import exercise_3_2
from exercise_3_3 import exercise_3_3


def main():
    # Ensure FrameNet v1.5 is available
    nltk.download("framenet_v15", quiet=True)

    print("=== Exercise 3.1 ===")
    exercise_3_1(fn)

    print("\n=== Exercise 3.2 ===")
    exercise_3_2(fn)

    print("\n=== Exercise 3.3 ===")
    exercise_3_3(fn)


if __name__ == "__main__":
    main()
