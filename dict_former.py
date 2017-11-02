import pymorphy2
morph = pymorphy2.MorphAnalyzer()


def transpose(word):
    if word[0].lower() == 'п':
        if 'NOUN' in morph.parse(word)[0].tag:
            new_word = morph.parse(word)[0].normal_form
            print(new_word)
        
        elif 'ADJF' in morph.parse(word)[0].tag:
            new_word = morph.parse(word)[0].inflect({'plur', 'gent'}).word
            print(new_word)

    if word[0].lower() == 'ц':
        if 'NOUN' in morph.parse(word)[0].tag:
            new_word = morph.parse(word)[0].inflect({'plur', 'gent'}).word
            print(new_word)
