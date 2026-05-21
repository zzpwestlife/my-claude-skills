.PHONY: pack check

DIST_DIR := ..
ZIP_NAME := skill-evolver.zip

pack: check
	@find . -name ".DS_Store" -delete
	@cd $(DIST_DIR) && zip -r $(ZIP_NAME) skill-evolver \
		-x "*.DS_Store" \
		-x "*/__pycache__/*" \
		-x "*/.pytest_cache/*" \
		-x "*/.git/*"
	@echo "$(DIST_DIR)/$(ZIP_NAME)"

check:
	@python3 scripts/check_skill_package.py . --json
	@python3 scripts/validate_dataset.py assets/example/dataset --json
