import copy
from collections import defaultdict
import sys
import os

sys.stdout = open(os.devnull, "w")

class KB:
	def __init__(self, sentences = None):
		self.predicates = list()
		self.poss = dict()
		self.negs = dict()
		self.sentences = copy.deepcopy(sentences)

	def look_inside_kb(self):
		print('\nSENTENCES: \n')
		for i, sentence in enumerate(self.sentences):
			print(i, sentence)

		print('\nALL PREDICATES: \n')
		print(self.predicates)

		print('\nPOSITIVE PREDICATES: \n')
		print(self.poss)

		print('\nNEGATIVE PREDICATES: \n')
		print(self.negs)

	def tell_KB(self):
		for i in range(len(self.sentences)):
			sent_string = self.sentences[i]
			splitList = sent_string.split('|')

			for x in splitList:
				s = self.returnPredicate(x)

				if '~' in s:
					if s not in self.predicates:
						self.predicates.append(s)
						self.negs[s] = [i]
					else:
						self.negs[s].append(i)
				else:
					if s not in self.predicates:
						self.predicates.append(s)
						self.poss[s] = [i]
					else:
						self.poss[s].append(i)

		self.standardiseVariables()
	
	def ask_KB(self, query):
		self.sentences.append(query)

		split_query = query.split('|')
		for p in split_query:
			s = self.returnPredicate(p)

			if '~' in s:
				if s not in self.predicates:
					self.predicates.append(s)
					self.negs[s] = [len(self.sentences)-1]
				else:
					self.negs[s].append(len(self.sentences)-1)
			else:
				if s not in self.predicates:
					self.predicates.append(s)
					self.poss[s] = [len(self.sentences)-1]
				else:
					self.poss[s].append(len(self.sentences)-1)

		complete = list()

		return self.fol_resolve(query, complete)

	def unify2(self, s, chars):
	    if len(chars) == 0:
	        return len(chars)
	    if len(s) == 0:
	        return len(s)

	    chars = set([c.lower() for c in chars])

	    words = s.split()
	    count = 0
	    for word in words:
	        valid = True
	        for char in word:
	            if char.isalnum() and char.lower() not in chars:
	                valid = False
	        if valid:
	            # print word
	            count += 1
	    return count

	def addSentenceToKB(self, sent, i):
		split_sent = sent.split('|')
		for x in split_sent:
			s = self.returnPredicate(x)
			if '~' in s:
				if s not in self.predicates:
					self.predicates.append(s)
					self.negs[s] = [i]
				else:
					self.negs[s].append(i)
			else:
				if s not in self.predicates:
					self.predicates.append(s)
					self.poss[s] = [i]
				else:
					self.poss[s].append(i)

	def standardiseVariables(self):
		for i in range(len(self.sentences)):
			sentence = self.sentences[i]
			terms = sentence.split('|')
			
			self.sentences[i] = ''
			
			for j in range(len(terms)):
				terms[j] = terms[j].strip()
				start = terms[j].index('(')
				end = terms[j].index(')')
				
				variables = terms[j][start+1:end].split(',')
				terms[j] = terms[j][:start+1]
				
				for k in range(len(variables)):
					if not any(char.isdigit() for char in variables[k]) and variables[k].islower():
						variables[k] = variables[k] + str(i)
					terms[j] += variables[k]
					if k == len(variables)-1:
						terms[j] += ')'
					else:
						terms[j] += ','
				
				self.sentences[i] += terms[j]
				if j != len(terms)-1:
					self.sentences[i] += '|'
	
	def returnPredicate(self, literal):
		literal = literal.strip()
		return literal[:literal.index('(')]

	def negateLiteral(self, s):
		return s[1:] if '~' in s else '~' + s

	def is_variable(self, x):
	    if len(x) == 1 and x.islower():
	        return True
	    elif x[0].islower():
	        return True
	    else:
	        return False

	def is_fact(self, goal):
	    for i in get_args(goal).split(","):
	        if is_variable(i):
	            return False
	    return True

	def getUnifiableMapping(self, query):
		terms = query.split('|')
		unify_dict = dict()

		for term in terms:
			term = term.strip()
			p = self.returnPredicate(term)
			neg_p = self.negateLiteral(p)

			if '~' in p:
				if neg_p in self.poss:
					unify_dict[p] = self.poss[neg_p]
			else:
				if neg_p in self.negs:
					unify_dict[p] = self.negs[neg_p]

		return unify_dict

	def unify(self, literal1, literal2):
		literal1 = literal1.strip()
		literal2 = literal2.strip()
		v1 = literal1[literal1.index('(')+1:-1].split(',')
		#print(v1)
		v2 = literal2[literal2.index('(')+1:-1].split(',')
		#print(v2)
		sub = dict()

		if len(v1) != len(v2):
			return None

		for i in range(len(v1)):
			v1[i] = v1[i].strip()
			v2[i] = v2[i].strip()

			if v1[i].islower():
				if not v2[i].islower():
					if v1[i] in sub:
						if v2[i] == sub[v1[i]]:
							sub[v1[i]] = v2[i]
						else:
							return None
					else:
						sub[v1[i]] = v2[i]
				else:
					if not v1[i] in sub and not v2[i] in sub:
						sub[v1[i]] = v2[i]
					elif v1[i] in sub and v1[i] != v2[i]:
						return None
			else:
				if v2[i].islower():
					if v2[i] in sub:
						if v1[i] == sub[v2[i]]:
							sub[v2[i]] = v1[i]
						else:
							return None
					else:
						sub[v2[i]] = v1[i]
				else:
					if v1[i] == v2[i]:
						sub[v2[i]] = v1[i]
					else:
						return None
		return sub

	def resolve(self, s1, s2, p):
		#print('Recursive call')
		print('Sentence1: ', s1)
		print('Sentence2: ', s2)
		print('Predicate: ', p)
		unify_term1 = list()
		unify_term2 = list()

		terms1 = s1.split('|')
		terms2 = s2.split('|')

		subst_ans, complete_i, complete_j = False, -1, -1

		for i in range(len(terms1)):
			check_p = self.returnPredicate(terms1[i])
			if check_p == self.negateLiteral(p):
				unify_term1.append(i)

		for i in range(len(terms2)):
			check_p = self.returnPredicate(terms2[i])
			if check_p == p:
				unify_term2.append(i)

		for i in range(len(unify_term1)):
			for j in range(len(unify_term2)):
				sub = {}
				sub = self.unify(terms1[unify_term1[i]], terms2[unify_term2[j]])
				if not sub:
					sub = self.unify(terms2[unify_term2[j]], terms1[unify_term1[i]])
				print(sub)
				if sub:
					complete_i = i
					complete_j = j
					subst_ans = True
					break

		if not subst_ans:
			return 'No subst', True
		
		#vars = any(s.isupper() for s in sub)

		vars = True
		for s in sub:
			if not sub[s].islower():
				vars = False
				break

		after_resol = ''

		#print('AA: ', terms1[unify_term1[complete_i]], terms2[unify_term2[complete_j]])
		del terms1[unify_term1[complete_i]]
		del terms2[unify_term2[complete_j]]

		for i in range(len(terms1)):
			t = terms1[i].strip()
			start = t.index('(')
			after_resol += t[:start+1]
			_vars = t[start+1:-1].split(',')

			for j in range(len(_vars)):

				v = _vars[j]
				if v in sub:
					after_resol += sub[v]
				else:
					after_resol += v

				if j == len(_vars)-1:
					after_resol += ')'
				else:
					after_resol += ','

			if i != len(terms1)-1:
				after_resol += '|'

		print("Intermediate after_resol: ", after_resol)

		for i in range(len(terms2)):
			if i == 0 and after_resol != '':	
				after_resol += '|'

			t = terms2[i].strip()
			start = t.index('(')
			after_resol += t[:start+1]
			_vars = t[start+1:-1].split(',')

			for j in range(len(_vars)):
				v = _vars[j]
				if v in sub:
					after_resol += sub[v]
				else:
					after_resol += v

				if j == len(_vars)-1:
					after_resol += ')'
				else:
					after_resol += ','

			if i != len(terms2)-1:
				after_resol += '|'

		print("after_resol: ", after_resol)

		after_resol = self.factorize(after_resol)

		if after_resol == '':
			#print('No')
			return 'Empty', True
		else:
			return after_resol, vars

	def factorize(self, after_resol):
		if not after_resol:
			return ''

		split_after_resol = after_resol.split('|')

		global_dict = dict()

		res = []

		for i in range(len(split_after_resol)):
			print(split_after_resol[i])
			pred1 = self.returnPredicate(split_after_resol[i])
			_vars2 = split_after_resol[i][split_after_resol[i].index('(')+1:-1].split(',')

			for j in range(i + 1, len(split_after_resol)):
				pred2 = self.returnPredicate(split_after_resol[j])
				_vars2 = split_after_resol[j][split_after_resol[j].index('(')+1:-1].split(',')

				if pred1 == pred2:
					local_dict = self.unify(split_after_resol[i], split_after_resol[j])
					if local_dict:
						global_dict.update(local_dict)

		for i in range(len(split_after_resol)):
			res_string = ''
			start = split_after_resol[i].index('(')
			res_string += split_after_resol[i][:start+1]
			vars_ = split_after_resol[i][start+1:-1].split(',')

			for j in range(len(vars_)):
				v = vars_[j]

				if v in global_dict:
					res_string += global_dict[v]
				else:
					res_string += v

				if j == len(vars_) - 1:
					res_string += ')'
				else:
					res_string += ','

			res.append(res_string)

		res = list(set(res))

		return '|'.join(res)



	def checkNoVariables(self, num_sent):
		sentence = self.sentences[num_sent]
		literals = sentence.split('|')

		for literal in literals:
			literal = literal.strip()
			variables = literal[literal.index('(')+1:-1].split(',')

			for v in variables:
				if v.islower():
					return False

		return True

	def fol_resolve(self, query, complete):
		l_complete = copy.deepcopy(complete)
		unify_dict = self.getUnifiableMapping(query)

		if not unify_dict:
			return False
			
		for predicate in unify_dict:
			for num_sent in unify_dict[predicate]:

				if num_sent in complete:
					continue

				sent, vars = self.resolve(self.sentences[num_sent], query, predicate)
				print("NEWSENT: ", sent)

				if sent == 'Empty':
					return True

				if sent == 'No subst':
					continue

				if not vars:
					if not self.checkNoVariables(num_sent):
						print('\nAppending: ', self.sentences[num_sent])
						l_complete.append(num_sent)
				
				# Recursive call
				ans = self.fol_resolve(sent, l_complete)

				if ans:
					return True

				if not vars:
					if not self.checkNoVariables(num_sent):
						del l_complete[-1]
		return False

def preprocess_sentences(sentences):
	pos_mapping = [[] for _ in range(len(sentences))] 
	neg_mapping = [[] for _ in range(len(sentences))]

	for i, sentence in enumerate(sentences):
		split_sentence = sentence.split('|')
		pos_set = set()
		neg_set = set()
		for s in split_sentence:
			if '~' in s.strip():
				neg_mapping[i].append(s.strip()[1:])
			else:
				pos_mapping[i].append(s.strip())

	res = []

	for i, pos in enumerate(pos_mapping):
		for neg in neg_mapping:
			for elem in pos:
				if elem in neg:
					pos.remove(elem)
					neg.remove(elem)

	print(pos_mapping)
	print(neg_mapping)

	for pos, neg in zip(pos_mapping, neg_mapping):
		if len(pos) > 0 and len(neg) > 0:
			res.append('|'.join(pos) + '|~' + '|~'.join(neg))
		elif len(pos) > 0:
			res.append('|'.join(pos))
		elif len(neg) > 0:
			res.append('|~'.join(neg))

	return res

def negate_literal(literal):
	if '~' in literal:
		negated_literal = literal[1:]
	else:
		negated_literal = '~' + literal
	return negated_literal.strip()

if __name__ == '__main__':

	kb1 = KB()
	print(kb1.unify('P(y, z)', '~P(x, x)'))

	with open ('input.txt', 'r') as f:

		file_data = f.readlines()
		num_queries = int(file_data[0].strip())
		queries = list()

		for i in range(num_queries):
			queries.append(file_data[i+1].strip())

		num_sentences = int(file_data[num_queries+1].strip())
		sentences = list()

		for i in range(num_sentences):
			temp = file_data[num_queries+2+i]

			split_sentence = temp.split('=>')

			if len(split_sentence) > 1:
				left, right = split_sentence

				split_left = left.split('&')
 
				negated_split_left = [ negate_literal(x.strip()) for x in split_left ]

				disjunction = negated_split_left + [right.strip()]

				sentString = '|'.join(disjunction)
			else:
				sentString = temp

			sentences.append(sentString.strip())

		# sentences = preprocess_sentences(sentences)
		# for sentence in sentences:
		# 	print(sentence)
		#sentences.sort(key = len)
		with open ('output.txt', 'w') as outfile:

			outstring = ''
			for q in queries:
				kb = KB(sentences)
				kb.tell_KB()

				#kb.look_inside_kb()

				query = kb.negateLiteral(q)
				answer = kb.ask_KB(query)

				if answer:
					print("ANSWER: TRUE")
					outstring += 'TRUE\n'
				else:
					print("ANSWER: FALSE")
					outstring += 'FALSE\n'

			outfile.write(outstring.strip())




