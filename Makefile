REPONAME=digital-crimes/requeue
BUILDROOT=$(HOME)/dockerbuild/$(REPONAME)
DOCKERREPO=docker-dcu-local.artifactory.secureserver.net/requeue
DATE=$(shell date)
BUILD_BRANCH=origin/main
SHELL=/bin/bash

define build_k8s
	kustomize edit set env BUILD_DATE=$(DATE)
	docker build -t $(DOCKERREPO):$(2) $(BUILDROOT)
endef

define deploy_k8s
	docker push $(DOCKERREPO):$(2)
	kubectl --context $(1)-dcu apply -k $(BUILDROOT)/k8s/$(1)/ --record
endef

all: env

env:
	pip install -r requirements.txt

.PHONY: flake8
flake8:
	@echo "----- Running linter -----"
	flake8 --config ./.flake8 .

.PHONY: isort
isort:
	@echo "----- Optimizing imports -----"
	isort -rc --atomic .

.PHONY: tools
tools: flake8 isort

.PHONY: test
test:
	@echo "----- Running tests -----"
	nosetests tests

.PHONY: testcov
testcov:
	@echo "----- Running tests with coverage -----"
	nosetests tests --with-coverage --cover-erase --cover-package=categorizer

.PHONY: prep
prep: tools
	@echo "----- preparing $(REPONAME) build -----"
	# copy the app code to the build root
	mkdir -p $(BUILDROOT)
	cp -rp ./* $(BUILDROOT)

.PHONY: prod
prod: prep
	@echo "----- building $(REPONAME) prod -----"
	read -p "About to build production image from $(BUILD_BRANCH) branch. Are you sure? (Y/N): " response ; \
	if [[ $$response == 'N' || $$response == 'n' ]] ; then exit 1 ; fi
	if [[ `git status --porcelain | wc -l` -gt 0 ]] ; then echo "You must stash your changes before proceeding" ; exit 1 ; fi
	git fetch && git checkout $(BUILD_BRANCH)
	$(eval COMMIT:=$(shell git rev-parse --short HEAD))
	$(call build_k8s,prod,$(COMMIT))
	git checkout -

.PHONY: dev
dev: prep
	@echo "----- building $(REPONAME) dev -----"
	$(call build_k8s,dev,dev)

.PHONY: ote
ote: prep
	@echo "----- building $(REPONAME) $(BUILD_VERSION) -----"
	$(call build_k8s,dev,dev)

.PHONY: prod-deploy
prod-deploy: prod
	@echo "----- deploying $(REPONAME) prod -----"
	$(call deploy_k8s,prod,$(COMMIT))

.PHONY: dev-deploy
dev-deploy: dev
	@echo "----- deploying $(REPONAME) dev -----"
	$(call deploy_k8s,dev,dev)

.PHONY: ote-deploy
ote-deploy: ote
	@echo "----- deploying $(REPONAME) ote -----"
	$(call deploy_k8s,ote,ote)

.PHONY: clean
clean:
	@echo "----- cleaning $(REPONAME) app -----"
	rm -rf $(BUILDROOT)