#Edit distnace algorithm
import string


def recursive_edit_distance(s1, s2, l1, l2):

	#check for the last char, if same then ignore
	#print('S1:', s1, l1)
	#print('S2:', s2, l2)

	#stopping condition
	if l1 == 0:
		return l2
	if l2 == 0:
		return l1

	if s1[l1-1] == s2[l2-1]:
		return recursive_edit_distance(s1, s2, l1-1, l2-1)
	else:
		return 1 + min(
					recursive_edit_distance(s1, s2, l1, l2-1),
					recursive_edit_distance(s1, s2, l1-1, l2),
					recursive_edit_distance(s1, s2, l1-1, l2-1),
					)

def edit_distance(s1, s2):
	s1 = list(s1.strip().lower())
	s2 = list(s2.strip().lower())
	

	l1 = len(s1)
	l2 = len(s2)

	x = recursive_edit_distance(s1, s2, l1, l2)

	return x



s1 = 'PRATIK'
s2 = 'MUNOT'
results = edit_distance(s1, s2)
print(results)



