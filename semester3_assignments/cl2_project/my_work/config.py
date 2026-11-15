
SEED = 42

# CORRECTION 1: Changed NEGATION_SHIFT from 4.0 to 1.5 to match the -1.0 to +1.0 lexicon scale
NEGATION_SHIFT = 1.5

INTENSIFIERS = {
    "very": 1.5,
    "extremely": 1.7,
    "utterly": 1.8,
    "really": 1.3,
    "slightly": 0.5,
    "somewhat": 0.7,
    "barely": 0.5,
    "quite": 1.2
}

IRREALIS = {
    "would",
    "could",
    "should",
    "might",
    "may",
    "if",
    "hope",
    "expect"
}

IRREALIS_FACTOR = 0.35
