compile_java:
	cd python && mkdir -p classes && javac *.java org/json/*.java -d classes

data/babynames.csv:
	curl https://raw.github.com/hadley/data-baby-names/master/baby-names.csv -o data/babynames.csv

data/babynames.txt: data/babynames.csv
	sed "1d" data/babynames.csv | awk -F, '{print $$2}' | \
	sed 's/"//g' > data/babynames.txt

.PHONY: setup
setup: compile_java data/babynames.txt

.PHONY: run
run:
	cd python && python NER.py ../data/train ../data/dev
