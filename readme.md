# Fluxus API

This repository contains all the files used while developing the API as part of my master's dissertation. Please use the "submission" branch.

---

The Api can be accessed at [http://fluxusml.com/](http://fluxusml.com/){service_name}/{endpoint}

---

## Folder structure

📂

├─ 📂  deployments

└── 📂 src

   ├── 📂 compute

   ├── 📂 database

     │ └── 📂 app

         │ ├── 📂 gql

         │ └── 📂 neo4j

   ├── 📂 math

     │ └── 📂 tests

   ├── 📂 pandas

     │ └── 📂 tests

   ├── 📂 timetests

   ├── 📂 visualisation

   └── 📂 worker

The Kubernetes resource files can be found in the "deployments" folder.

The "src" folder contains all the microservices, each in a separate folder. The "timetests" folder contains the files used for timing the "compute" service. Each folder contains a Dockerfiles used to create the container image. Each folder also contains the necessary Pipfiles for creating a Python environment using Pipenv.

---

## Contact

Robert Marincu

rsm43@bath.ac.uk