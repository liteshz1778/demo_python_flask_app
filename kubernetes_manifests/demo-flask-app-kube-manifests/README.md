# 🚀 Flask Web Application Deployment on Kubernetes with MySQL

## 📌 Overview

This project demonstrates the deployment of a **Flask Web Application with MySQL Database** on Kubernetes.

The application stack includes:

- 🐍 Flask Web Application
- 🐬 MySQL Database
- 💾 Persistent Storage using PV/PVC
- 🔐 Kubernetes Secrets for database credentials
- ⚙️ ConfigMap for application configuration
- 📦 StatefulSet for MySQL deployment
- 🌐 Kubernetes Services for application communication
- 🤖 Shell scripts for automated deployment and cleanup

---

# 🏗️ Architecture Flow

```
                Users
                  |
                  |
            Kubernetes Service
                  |
                  |
      +-------------------------+
      |   Flask Web Application |
      |     Deployment         |
      +-------------------------+
                  |
                  |
          Kubernetes Service
                  |
                  |
      +-------------------------+
      |     MySQL Database      |
      |       StatefulSet       |
      +-------------------------+
                  |
                  |
          Persistent Storage
                  |
      +-------------------------+
      | Persistent Volume (PV)  |
      | Persistent Volume Claim |
      +-------------------------+

```

---

# 📂 Repository Structure

```

.
├── automate_deployment
│ ├── create_resources.sh
│ └── delete_resources.sh
│
├── deployment-svc-webapp-flask.yaml
│ └── Flask Application Deployment + Service
│
├── host-pv.yaml
│ └── Persistent Volume configuration
│
├── msqldb-secret.yaml
│ └── MySQL database credentials
│
├── mysql-sc.yaml
│ └── Storage Class configuration
│
├── sts-headless-svc-mysqldb.yaml
│ └── MySQL StatefulSet + Headless Service
│
└── webapp-cm.yml
└── Flask application configuration


```

---

# 🔧 Kubernetes Components


## 🐍 Flask Web Application

File:

deployment-svc-webapp-flask.yaml

Creates:

- Kubernetes Deployment
- Application Pods
- Service for exposing Flask application


Features:

✅ Containerized Flask application
✅ Replica management
✅ Service discovery
✅ Application connectivity with MySQL


---

## 🐬 MySQL Database

File:


sts-headless-svc-mysqldb.yaml


Creates:

- MySQL StatefulSet
- Headless Service


Why StatefulSet?

- Stable network identity
- Persistent storage association
- Database workload management


---

## 💾 Persistent Storage


Files:


host-pv.yaml
mysql-sc.yaml

Provides:

- Persistent Volume
- Storage Class
- Data persistence after pod restart


Storage Flow:

```
MySQL Pod
|
|
PersistentVolumeClaim
|
|
PersistentVolume
|
|
Host Storage
```

---

## 🔐 Database Credentials


File:

msqldb-secret.yaml


Stores sensitive information:

- MySQL Username
- MySQL Password
- Database Name


Consumed by:

MySQL StatefulSet
Flask Application

---

## ⚙️ Application Configuration


File:

webapp-cm.yml


Contains application configuration values:

Example:

- Database host
- Database port
- Application settings


Mounted into Flask application using Kubernetes ConfigMap.

---

# 🚀 Deployment Automation


Directory:

automate_deployment


Contains:

## Create Resources

File:

create_resources.sh


Deploys complete Kubernetes stack:


```
bash ./create_resources.sh

Resources created:

StorageClass
      |
PersistentVolume
      |
MySQL StatefulSet
      |
MySQL Service
      |
Flask Deployment
      |
Flask Service
```

## Delete Resources

File:

delete_resources.sh

Cleanup Kubernetes resources:

bash ./delete_resources.sh


---

📚 Kubernetes Concepts Covered

✅ Deployments
✅ StatefulSets
✅ Services
✅ Headless Services
✅ Persistent Volumes
✅ Persistent Volume Claims
✅ Storage Classes
✅ ConfigMaps
✅ Secrets
✅ Automated Kubernetes Deployment

---

👨‍💻 Author

Litesh Zadane

🚀 DevOps Engineer | SRE | Cloud & Platform Engineer

GitHub:
https://github.com/liteshz1778
