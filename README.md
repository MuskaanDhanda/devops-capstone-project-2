# DevOps Capstone Project 2

Standalone architecture for Project 2, based on the provided specifications.

<!-- OVERVIEW:START -->
| # | Component | Project file | Topics covered |
|---|-----------|--------------|----------------|
| 1 | Architecture | [Project 2 Architecture](architecture.png) | Terraform, Ansible, Jenkins, Docker, Kubernetes, AWS EC2 |
<!-- OVERVIEW:END -->

## Architecture

![Project 2 architecture](architecture.png)

## Components

- **Terraform** creates AWS infrastructure, including VPC and EC2 resources.
- **Ansible** configures the servers.
- **Four EC2 workers:**
  - Worker 1: Jenkins and Java
  - Worker 2: Docker and Kubernetes
  - Worker 3: Java, Docker, and Kubernetes
  - Worker 4: Docker and Kubernetes
- **GitHub Master branch** sends a webhook to Jenkins when code is committed.
- **Jenkins pipeline:** Build, Test, and Prod stages.
- **Build:** Jenkins checks out the source, builds a custom Docker image using a Dockerfile, and pushes it to Docker Hub.
- **Test:** Deploys to the test server and runs application tests.
- **Production:** Monthly release on the 25th; deploys to Kubernetes with 2 replicas and exposes the application through NodePort `30008`.

## Project files

<!-- PROJECT-FILES:START -->
| File / Folder | What's inside |
|---------------|---------------|
| [architecture.png](architecture.png) | Project 2 architecture diagram |
<!-- PROJECT-FILES:END -->

## Adding files to the project

Both tables above update automatically. When you add, delete or rename a file or folder, the [Update README tables](.github/workflows/update-readme.yml) workflow adds or removes its linked row in both tables. Edits to existing files don't touch the README.

New rows get an automatic description. To change one, edit the text in the table; the workflow keeps your wording.
