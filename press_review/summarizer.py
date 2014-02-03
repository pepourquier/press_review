#!/usr/bin/python
# -*- coding: utf-8 -*-
import summarize
from text.blob import TextBlob
import nltk
from nltk.corpus import wordnet
import random

input = u"""
A charge sheet was filed Monday against two Arabs from Issawiya, in Jerusalem, who are accused of taking part in a the stabbing of a Jewish man, Moshe Limoi, immediately after Tisha B'Av. The attack took place near the Damascus Gate, as Limoi was going home from evening prayers at the Kotel.

The two are Sultan Abu Humus, 19, and Mahmoud Rajbi, 18. Abu Humus and another man stabbed Limoi – one from the front and the other from the back. He was wounded in the chest, thigh and arm. Rajbi served as lookout during this time, to make sure that security forces are not anywhere near.

The three then took a sherut cab to Issawiya. They urged the driver to hurry up and start driving immediately, and promised him that they would pay him for the empty places in the cab. When they arrived at Issawiya, Abu Humus gave his clothes to his sister, who was supposed to “make them disappear.”

He also went with the third man to a barber shop in order to make themselves less recognizable to the victim. Abu Humus is accused of attempted murder and attempts to interfere with the judicial process, and Rajbi is accused of aggravated assault.

Describing his experience to visiting MKs in July, the victim recalled:

"The terrorist stuck the knife in me and turned it around. I said 'Shema Yisrael' and other prayers one says” when they think they are about to die.

“I walked up the stairs and by mistake called the police instead of Magen David Adom. I saw a patrol and they tended to my wounds right away. All the Arabs in the area just stopped and stared, and no one was interested in what happened to me,” he added.
"""

def get_summary(text, compression):
    ss = summarize.SimpleSummarizer()
    return ss.summarize(text, 2)

def show_words(text):
    sentences = nltk.sent_tokenize(text)
    for sentence in sentences:
        print(nltk.word_tokenize(sentence))

 
def spin(content):
    """takes a string like
 
    {Hi|Hello|Good morning}, my name is Matt and I have {something {important|special} to say|a favorite book}.
 
    and randomly selects from the options in curly braces
    to produce unique strings.
    """
    start = content.find('{')
    end = content.find('}')
 
    if start == -1 and end == -1:
        #none left
        return content
    elif start == -1:
        return content
    elif end == -1:
        raise "unbalanced brace"
    elif end < start:
        return content
    elif start < end:
        rest = spin(content[start+1:])
        end = rest.find('}')
        if end == -1:
            raise "unbalanced brace"
        return content[:start] + random.choice(rest[:end].split('|')) + spin(rest[end+1:])


#Looking for each synonym
def get_syn_list(word):
    wiki = TextBlob(word)
    syn_list = ''
    if 'NN' or 'VBZ' in wiki.tags:
        if len(word) >= 4:
            syn_list = '{'+word+'|'
            words = wordnet.synsets(word)
            for c, w in enumerate(words):
                if c <= 2:
                    for i, s in enumerate(w.lemmas):
                        if i <= 3:
                            if '_' not in s.name and s.name != word and s.name != word.title() and s.name.title() != word:
                                syn_list += s.name + '|'
            syn_list = syn_list[:-1]
        syn_list += '}'
        return syn_list

def get_text_synonymizer(text):
    sentences = nltk.sent_tokenize(text)
    for sentence in sentences:
        words = nltk.word_tokenize(sentence)
        for word in words:
            if len(word) > 3:
                text = text.replace(' '+word, ' '+get_syn_list(word))
    return text

#input=ss.summarize(input, 2)
#print(spin(get_text_synonymizer(input)))
                    
