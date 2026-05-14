.PHONY: all dep unittest static-check nil-check lint test tools

# Default target
all: dep lint test

# Install dependencies
dep:
	@echo "ensure dependencies..."
	@go mod tidy

# Install tools
tools:
	@echo "installing tools..."
	@go install gotest.tools/gotestsum@latest
	@go install honnef.co/go/tools/cmd/staticcheck@latest
	@go install go.uber.org/nilaway/cmd/nilaway@latest

# Test
test: unittest

unittest: dep
	@echo "gosum test..."
	@time CGO_CFLAGS=-Wno-undef-prefix gotestsum --packages="`go list ./... | grep -v stub_test`" -- -count=1 -failfast -gcflags="all=-l -N"

# Lint
lint: static-check nil-check

static-check:
	@echo "run static check..."
	@staticcheck -checks="all","-ST1000","-ST1003","-ST1016","-ST1020","-ST1021","-ST1022","-SA1019" -tests=false -f=text `go list ./... | grep -E -v "cmd|stub_test|pb|client"`

nil-check:
	@echo "run nil check..."
	@nilaway ./internal/app/...
