.PHONY: docker local latest

VERSION := 1.0.0
DOCKER_PLATFORMS := linux/amd64,linux/arm64,linux/arm/v7

docker:
	docker buildx build . \
      -f Dockerfile \
      --platform $(DOCKER_PLATFORMS) \
      -t synesthesiam/wyoming-opentts:$(VERSION)

latest:
	docker buildx build . \
      -f Dockerfile \
      --platform $(DOCKER_PLATFORMS) \
      -t synesthesiam/wyoming-opentts:$(VERSION) \
      -t synesthesiam/wyoming-opentts:latest \
      --push

local:
	docker buildx build . \
      -f Dockerfile \
      -t synesthesiam/wyoming-opentts:$(VERSION) --load
