import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer
import string


def load_text_normalization_objects(raw_wine_dataset):
    # load the snowball stemmer
    sno = SnowballStemmer('english')

    # load the file that contains the full table of descriptor mappings
    descriptor_mapping = pd.read_csv('chardonnay_descriptors.csv')
    descriptor_mapping.set_index('descriptor_raw', inplace=True)

    # load a table with all possible punctuation
    punctuation_table = str.maketrans({key: None for key in string.punctuation})

    # load all the unknowable tokens: stopwords and custom wine-related terms
    stopwords = open("stopwords_extended.txt").read().splitlines()

    unknowable_identifiers = (' '.join(list(set(raw_wine_dataset['Variety'].dropna())))
                              + ' '.join(list(set(raw_wine_dataset['Country'].dropna())))
                              # + ' '.join(list(set(raw_wine_dataset['Province'].dropna())))
                              # + ' '.join(list(set(raw_wine_dataset['Region'].dropna())))
                              # + ' '.join(list(set(raw_wine_dataset['Subregion'].dropna())))
                              # + ' '.join(list(set(raw_wine_dataset['Winery'].dropna())))
                              # + ' '.join(list(set(raw_wine_dataset['Designation'].dropna())))
                              ).split(' ')

    lower_case_unknowables = [str.lower(word) for word in unknowable_identifiers]

    unknowable_tokens = stopwords + lower_case_unknowables

    return sno, descriptor_mapping, punctuation_table, unknowable_tokens


def token_normalization(tokenized_word, sno, punctuation_table, unknowable_tokens):
    # this function tokenizes our wine description, converts all text to lower case, removes punctuation,
    # removes digits and removes any 'unknowable' tokens
    lower_case_word = str.lower(tokenized_word)
    if lower_case_word not in unknowable_tokens:
        lemmatized_word = sno.stem(lower_case_word)
        normalized_word = lemmatized_word.translate(punctuation_table)
        if normalized_word is not None and len(str(normalized_word)) > 1 and not normalized_word.isdigit():
            return normalized_word
        else:
            return None


def generate_bigrams(list_of_tokens):
    list_of_bigrams = []
    for i in range(len(list_of_tokens) - 1):
        first_word = list_of_tokens[i]
        second_word = list_of_tokens[i + 1]
        if first_word != second_word:
            bigram = first_word + ' ' + second_word
            list_of_bigrams.append(bigram)
    return list_of_bigrams


def map_descriptors(list_of_descriptors, descriptor_mapping, descriptor_mapping_level):
    updated_list_of_descriptors = []
    descriptor_level_mapping = 'descriptor_level_' + str(descriptor_mapping_level)

    for term in list_of_descriptors:
        if term in list(descriptor_mapping.index) and term not in updated_list_of_descriptors:
            updated_list_of_descriptors.append(descriptor_mapping.loc[term, descriptor_level_mapping])

    return updated_list_of_descriptors


def full_text_normalization(wine_description, sno, descriptor_mapping, punctuation_table, unknowable_tokens, descriptor_mapping_level=3):
    tokenized_words = word_tokenize(wine_description)
    normalized_tokens = []
    for word in tokenized_words:
        normalized_token = token_normalization(word, sno, punctuation_table, unknowable_tokens)
        normalized_tokens.append(normalized_token)
    normalized_tokens = [n for n in normalized_tokens if n is not None]
    normalized_text_bigrams = generate_bigrams(normalized_tokens)
    normalized_text_unigrams_bigrams = normalized_tokens + normalized_text_bigrams
    normalized_text_mapped_descriptors = map_descriptors(normalized_text_unigrams_bigrams, descriptor_mapping, descriptor_mapping_level)
    normalized_text_mapped_descriptors = list(set(normalized_text_mapped_descriptors))

    return normalized_text_mapped_descriptors


def return_word_mapping_dict(wine_description, sno, punctuation_table, unknowable_tokens):
    dict_normalization_mapping = {}
    tokenized_words = word_tokenize(wine_description)
    for word in tokenized_words:
        normalized_token = token_normalization(word, sno, punctuation_table, unknowable_tokens)
        if normalized_token not in dict_normalization_mapping:
            dict_normalization_mapping[normalized_token] = [word]
        else:
            if str(word) not in dict_normalization_mapping[normalized_token]:
                dict_normalization_mapping[normalized_token].append(word)

    return dict_normalization_mapping

# raw_wine_dataset = pd.read_csv('data/all_scraped_wine_info_chardonnay.csv', encoding="latin9")
# sno, descriptor_mapping, punctuation_table, unknowable_tokens = load_text_normalization_objects(raw_wine_dataset)
#
# wine_description = 'Marmalade, toffee, vanilla and tonka bean swirl on the nose. ' \
#                    'Rich and smooth, rounded and mellow, yet with an incredibly bright, ' \
#                    'aromatic core of fine citrus. Think dried and candied orange peel and candied blood orange. ' \
#                    'What a magical balance the citrus freshness strikes with the cushioning, gentle vanilla. ' \
#                    'Textural bliss and aromatic fireworks. Drink until 2040, at least.'
# normalized_description = full_text_normalization(wine_description, sno, descriptor_mapping, punctuation_table, unknowable_tokens)
# print(normalized_description)
