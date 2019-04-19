from sklearn.feature_extraction.text import TfidfVectorizer

doc1 = "I like apples. I like oranges too"
doc2 = "I like apples. I like doctors"
doc3 = "An apple a day keeps the doctor away"
doc4 = "Never compare an apple to an orang"

documents = [doc1, doc2, doc3, doc4]

tfidf = TfidfVectorizer().fit_transform(documents)
pairwise_sim = tfidf * tfidf.T

# https://stackoverflow.com/a/27220066
print(pairwise_sim.A)