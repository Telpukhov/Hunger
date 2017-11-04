import pymorphy2
import re
morph = pymorphy2.MorphAnalyzer()



def transpose(word):
    if word not in ['прош', 'перех', 'предик', 'прил', 'поряд']:
        if word[0] == 'п' or word[0] == 'П':
            if 'NOUN' in morph.parse(word)[0].tag:
                new_word = ''
                try:
                    new_word = morph.parse(word)[0].normal_form
                except:
                    None
                if new_word != '':
                    f = open('1.txt', 'a')
                    f.write(new_word + '\n')
                    f.close()
                return(new_word)
        elif word[0] == 'п' or word[0] == 'П':
            if 'ADJF' in morph.parse(word)[0].tag:
                new_word = ''
                try:
                    new_word = morph.parse(word)[0].inflect({'plur', 'gent'}).word
                except:
                    None
                if new_word != '':
                    f = open('2.txt', 'a')
                    f.write(new_word + '\n')
                    f.close()
                return(new_word)
        elif word[0] == 'ц' or word[0] == 'Ц':
            if 'NOUN' in morph.parse(word)[0].tag:
                new_word = ''
                try:
                    new_word = morph.parse(word)[0].inflect({'plur', 'gent'}).word
                except:
                    None
                if new_word != '':
                    f = open('3.txt', 'a')
                    f.write(new_word + '\n')
                    f.close()
                return(new_word)
        else:
            return None


def process_text(filename):
    with open(filename) as f:
        for line in f:
            for word in re.findall(r'\w+', line):
                res = transpose(word)
                if res != None:
                    print(res)


if __name__ == '__main__':
    process_text('morph.txt')