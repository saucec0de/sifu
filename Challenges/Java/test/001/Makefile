all: Hello.class

run:
	java Hello

%.class: %.java
	javac $^

clean:
	@rm -rf Hello.class
