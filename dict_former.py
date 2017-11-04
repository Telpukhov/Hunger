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
                    return(1, new_word)
        if word[0] == 'п' or word[0] == 'П':
            if 'ADJF' in morph.parse(word)[0].tag:
                new_word = ''
                try:
                    new_word = morph.parse(word)[0].inflect({'plur', 'gent'}).word
                except:
                    None
                if new_word != '':
                    return(2, new_word)
        if word[0] == 'ц' or word[0] == 'Ц':
            if 'NOUN' in morph.parse(word)[0].tag:
                new_word = ''
                try:
                    new_word = morph.parse(word)[0].inflect({'plur', 'gent'}).word
                except:
                    None
                if new_word != '':
                    return(3, new_word)
        else:
            return None


def process_text(filename):

    #f = open('1.txt')
    #text = f.read()
    #first = set(text.split('\n'))
    #f.close()
    #f = open('2.txt')
    #text = f.read()
    #second = set(text.split('\n'))
    #f.close()
    #f = open('3.txt')
    #text = f.read()
    #third = set(text.split('\n'))
    #f.close()
    first = set()
    second = set()
    third = set()
    with open(filename) as f:
        for line in f:
            for word in re.findall(r'\w+', line):
                res = transpose(word)
                if res != None:
                    print(res)
                    if res[0] == 1:
                        first.add(res[1])
                    elif res[0] == 2:
                        second.add(res[1])
                    elif res[0] == 3:
                        third.add(res[1])
    x_1 = '\n'.join(first)
    x_2 = '\n'.join(second)
    x_3 = '\n'.join(third)
    f = open('1.txt', 'a')
    f.write(x_1)
    f.close()

    f = open('2.txt', 'a')
    f.write(x_2)
    f.close()

    f = open('3.txt', 'a')
    f.write(x_3)
    f.close()


if __name__ == '__main__':
    process_text('OZHEGOV.TXT')