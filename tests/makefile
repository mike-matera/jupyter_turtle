TESTS = $(addprefix temp/,$(wildcard *.ipynb))

all: $(TESTS)

temp/%.ipynb: %.ipynb
	uv run jupyter nbconvert --to notebook --execute $< --output-dir temp

clean:
	rm -rf temp
