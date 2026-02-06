.PHONY: setup test spec-check

IMAGE_NAME := chimera-dev

setup:
	@docker build -t $(IMAGE_NAME) .

test: setup
	@docker run --rm $(IMAGE_NAME) pytest -q

spec-check:
	@python -c "import pathlib; assert pathlib.Path('specs/_meta.md').exists(); assert pathlib.Path('specs/functional.md').exists(); assert pathlib.Path('specs/technical.md').exists(); print('spec-check: OK')"
