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
	cd k8s/$(1) && kustomize edit set image $(DOCKERREPO):$(2)
	kubectl --context $(1)-cset apply -k k8s/$(1)/ --record
	cd k8s/$(1) && kustomize edit set image $(DOCKERREPO):$(1)
endef

all: init

init:
	pip install -r test_requirements.txt
	pip install -r requirements.txt

.PHONY: lint
lint:
	isort -rc --atomic .
	flake8 --config ./.flake8 .

.PHONY: unit-test
unit-test:
	@echo "----- No unit tests to run-----"

.PHONY: testcov
testcov:
	@echo "----- No tests to run for coverage-----"

.PHONY: prep
prep: lint
	@echo "----- preparing $(REPONAME) build -----"
	# copy the app code to the build root
	mkdir -p $(BUILDROOT)
	cp -rp ./* $(BUILDROOT)

.PHONY: prod
prod: prep
	@echo "----- building $(REPONAME) prod -----"
	read -p "About to deploy a production image. Are you sure? (Y/N): " response ; \
	if [[ $$response == 'N' || $$response == 'n' ]] ; then exit 1 ; fi
	if [[ `git status --porcelain | wc -l` -gt 0 ]] ; then echo "You must stash your changes before proceeding" ; exit 1 ; fi
	$(eval COMMIT:=$(shell git rev-parse --short HEAD))
	$(call build_k8s,prod,$(COMMIT))

.PHONY: dev
dev: prep
	@echo "----- building $(REPONAME) dev -----"
	$(call build_k8s,dev,dev)

.PHONY: ote
ote: prep
	@echo "----- building $(REPONAME) $(BUILD_VERSION) -----"
	$(call build_k8s,ote,ote)

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