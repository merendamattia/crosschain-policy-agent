# [1.2.0](https://github.com/merendamattia/crosschain-policy-agent/compare/v1.1.1...v1.2.0) (2025-10-17)


### Features

* add GitHub Actions workflow to push Docker image to Docker Hub ([1fff679](https://github.com/merendamattia/crosschain-policy-agent/commit/1fff679caaf4e1e23061bde4ac78b08fa44066b3))

## [1.1.1](https://github.com/merendamattia/crosschain-policy-agent/compare/v1.1.0...v1.1.1) (2025-10-17)


### Bug Fixes

* filter out policies with no events after merging ([26a642a](https://github.com/merendamattia/crosschain-policy-agent/commit/26a642af7f3af70566cf5d47cb937b2f6c056236))

# [1.1.0](https://github.com/merendamattia/crosschain-policy-agent/compare/v1.0.0...v1.1.0) (2025-10-17)


### Bug Fixes

* remove unnecessary exception handling in main function ([acc126e](https://github.com/merendamattia/crosschain-policy-agent/commit/acc126e96657e5f407de578c8d3ff42e82078ec1))


### Features

* implement client registry for LLM providers and update app to use it ([49e4f1f](https://github.com/merendamattia/crosschain-policy-agent/commit/49e4f1fc440615593fc025e8d27f14243ac19d43))

# 1.0.0 (2025-10-16)


### Bug Fixes

* improve prompt loading logic in main function ([badf341](https://github.com/merendamattia/crosschain-policy-agent/commit/badf3415d00701d3bc6f6c3186a2acc0480fc78d))
* standardize workflow names for consistency ([16a097a](https://github.com/merendamattia/crosschain-policy-agent/commit/16a097a2c077c353aafec54c94b72aea2ddbc487))


### Features

* add datapizza-ai dependency to requirements ([4bf00be](https://github.com/merendamattia/crosschain-policy-agent/commit/4bf00be4d7e3c77b6731988644a145146dbc3c63))
* add datapizza-ai-clients-google dependency to requirements ([89cec4e](https://github.com/merendamattia/crosschain-policy-agent/commit/89cec4e704416706d0baf4d82aa6031d8c313b7d))
* add Dockerfile and .dockerignore for containerization ([7c6d483](https://github.com/merendamattia/crosschain-policy-agent/commit/7c6d483a37ec9566f1f945cc675f5d0857aa316b))
* add GitHub Actions workflow for Python tests ([2212c9d](https://github.com/merendamattia/crosschain-policy-agent/commit/2212c9d841a19ed2a669142b7a871dd7398b88fb))
* add initial implementation of policy agent with environment configuration and prompt handling ([90308fe](https://github.com/merendamattia/crosschain-policy-agent/commit/90308fe85c395101cb7579fa642958b70eb6fcd0))
* add initial test cases for formatter and tools modules ([cae77eb](https://github.com/merendamattia/crosschain-policy-agent/commit/cae77eb6c374b1c03327afed87e754c561989374))
* add pytest dependency to requirements ([af739cd](https://github.com/merendamattia/crosschain-policy-agent/commit/af739cdc819de0e17480570ce7c598bc3121870c))
* allow conventional commits check on develop branch ([e2851f0](https://github.com/merendamattia/crosschain-policy-agent/commit/e2851f0b0a67abec798e159983090bda4017f542))
* enhance CLI with command-line arguments for target path and output file, update environment configuration ([fe46080](https://github.com/merendamattia/crosschain-policy-agent/commit/fe46080ad0444ad3afa5650a909e9e6590651d33))
* enhance output file configuration in environment settings ([c63796a](https://github.com/merendamattia/crosschain-policy-agent/commit/c63796ae1e1e6ae758d39902f5e7f20a48d8d0de))
* implement AgentRunner and associated tools for processing Solidity files and generating policy JSON ([04bac5e](https://github.com/merendamattia/crosschain-policy-agent/commit/04bac5ee59e11d16d7e92400530787dfe546c71a))
