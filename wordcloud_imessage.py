import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
import sqlite3
import os
from bs4 import BeautifulSoup


def get_word_list(message_list):
	word_list = []
	db_text_lengths = []
	for i in message_list:
		if i==None:
			continue
		else:
			words = i.split(" ")
			for word in words:
				word_list.append(str(''.join([i if ord(i) < 128 else '' for i in word])).lower())
			db_text_lengths.append(len(words))
	return word_list, db_text_lengths


def run_wordcloud(filepath, min_wordlength=2, search_string=None, nwic=100, msg_type='TXT', fb_username=None):
	directory = '/Users/' + str(username) + '/Documents/wordcloud'
	if not os.path.exists(directory):
		print('Making wordcloud folder..')
		os.makedirs(directory)
	
	db_words = []
	c = 0

	if msg_type=='TXT':
		message_path ='/Users/'+str(username)+'/Library/Messages/chat.db'
		conn = sqlite3.connect(message_path)
		cur = conn.cursor()    
		cur.execute("SELECT * FROM 'message'")
		rows = cur.fetchall()

		for row in rows:
			db = row[2] #messages in column 2
			db_words.append(db)

	else:
		for file in os.listdir(directory + '/messages'):
			if file.endswith(".html"):
				soup = BeautifulSoup(open(directory + '/messages/' + file), "lxml")
				print('Reading ' + file)
				messages = soup.find_all('p')
				authors = soup.find_all('span')

				for m in xrange(len(messages)):
					if authors[m*2].get_text() == fb_username:
						if messages[m] != None:
							db_words.append(messages[m].get_text())
							c+=1
        print('Number of messages found under FB username ' + str(fb_username) + ': ' + str(c))    				
        
	word_list, db_text_lengths = get_word_list(db_words)

	#filter out URLs with very long strings
	word_list = [word for word in word_list if len(word) < 20]

	if search_string != 'None':
		word_list = [word for word in word_list if search_string in word]

	fig_directory = directory + '/figures'
	if not os.path.exists(fig_directory):
		print('Making directory to put figures into..')
		os.makedirs(fig_directory)

	plt.figure()
	plt.hist(db_text_lengths, histtype='step', bins = np.linspace(0, 100, 20), label='Total texts: ' + str(len(db_text_lengths)))
	plt.title('Distribution of number of words per text')
	plt.xlabel('Length of text (nwords)')
	plt.ylabel('log10(Number)')
	plt.xlim(0, 100)
	plt.yscale('log')
	plt.savefig(fig_directory + '/text_length_histogram.png')
	plt.close()


	word_counter = {}
	for word in word_list:
		if word in word_counter:
			word_counter[word] += 1
		else:
			word_counter[word] = 1


	popular_words = sorted(word_counter, key = word_counter.get, reverse = True)

	common_words = [ 'the', 'you', 'and',  'that',  'for','have', 'but', 'was',\
	         'all', 'But', 'this', 'with', 'I\'m', 'I\'ll', 'Yeah', 'like', 'can', 'good', \
	       'some', 'not', 'I\u2019m', 'It\'s', 'Are','are', 'Hey', 'The', 'That', 'can\u2019t','use' ]

	top_words = [word for word in popular_words if word not in common_words and len(word) > min_wordlength]
	counters = [word_counter[word] for word in top_words]
	tw = top_words[0:int(nwic)]

	if len(tw) == 0:
		print('No instances with search string \'' + str(search_string) + '\' found! try again.')
		return;

	if len(tw) < int(nwic):
		print('Not as many as you thought! Showing top ' + str(len(tw)) + ' occurrences.')
	else:
		print('Retrieval completed, results saved in ' + str(directory) + '/figures')


	filename_string = str(msg_type)
	if msg_type == 'FB':
		filename_string = filename_string +'_' + str(fb_username)
	filename_string = filename_string + '_top' + str(len(tw))
	if search_string != 'None':
		filename_string = filename_string + '_' + str(search_string)

	N = np.sum(counters)


	plt.figure(figsize=(13,13))
	for w in xrange(len(tw)):
		plt.text(np.random.uniform(0.05, 0.88), np.random.uniform(0.1, 0.9), tw[w], fontsize=100*(np.float32(counters[w])/np.float32(N))**0.25, rotation=np.random.uniform(-30, 30))
	plt.savefig(fig_directory + '/' + filename_string + '.png')
	plt.close()

## code for user input below

message_type = raw_input("iMessage or Facebook? (TXT for iMessage, FB for Facebook): ")

# username
good_input = 0
username = raw_input("Enter computer username: ")

if message_type == 'FB':
	fb_username = raw_input("Enter Facebook username: ")

while good_input == 0:
	if message_type == 'TXT':
		if os.path.exists('/Users/' + str(username)):
			good_input = 1
		else:
			username = raw_input("That doesn't seem to be your username, try again! (Ctrl-C to quit, but don't) ")
	else:
		good_input = 1

# minimum word length
good_input = 0
minword = raw_input("Minimum length of words (default 3): ")
while good_input == 0:
	if minword.isdigit():
		good_input = 1
		minword = int(minword)
	else:
   		minword = raw_input("That's not an integer! Try again: ")

# search string
search = raw_input("Any particular search string? (None if no particular search): ")
ntopwords = raw_input("Top ___ words? ")

good_input = 0
while good_input == 0:
	if ntopwords.isdigit():
		good_input = 1
		ntopwords = int(ntopwords)
	else:
   		ntopwords = raw_input("That's not an integer! Try again: ")

if message_type == 'TXT':
	run_wordcloud(username, minword, search, ntopwords, message_type)
elif message_type == 'FB':
	run_wordcloud(username, minword, search, ntopwords, message_type, fb_username)


print('Your wordcloud should be located in /Users/' + str(username) + '/Documents/wordcloud.')



