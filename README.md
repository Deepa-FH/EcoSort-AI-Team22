# EcoSort AI — AI-Powered Waste Sorting & Recycling Assistant

**Python Compact Programming · Group 22 · FH Dortmund**

Welcome to the main repository for **EcoSort AI** (also referred to as *Sortly AI*), an AI-powered waste sorting and recycling assistant designed to help users identify waste items, navigate German bin rules, and track recycling analytics.

> **Note on Repository Structure:** This `main` branch serves as the central directory and overview for the repository. The complete source code, deliverables, and implementations are organized across dedicated branches corresponding to each Home Assignment (Homeworkassignment001–Homeworkassignment004) and the final Capstone project(Capstone-Project).

---

## Team 22 & Subsystem Ownership

| Team Member | Matriculation No. | Subsystem / Responsibility |
| :--- | :---: | :--- |
| **Deepa Halapeti** | 7225894 | Dataset & Preprocessing |
| **Prasad Hule** | 7225861 | AI Image Recognition (YOLO) |
| **Mayuresh Kumbhar** | 7226310 | Recycling Rules & Ask AI (LLM Integration) |
| **Vijay Kathiresan** | 7226794 | Web App, Dashboard & Integration |

---

## Repository Branches Overview

Switch to any of the branches below to inspect the code, run the applications, or review the documentation for specific milestones:

| Branch / Milestone | Focus Area | Key Technologies & Concepts | Presentation Video |
| :--- | :--- | :--- | :---: |
| **`Capstone-Project`** *(Final Project)* | Full-stack production application integrating YOLO, German recycling rules, multimodal LLM fallback, SQLite persistence, and role-based web dashboard. | Python, Flask, YOLOv8, SQLite, Docker, KIconnect LLM, Pytest (54 tests) | [Watch Video](https://youtu.be/KSPYhftteHU?is=rGCiBpW-NYKTg029) |
| **`Homeworkassignment001`** *(Home Task 1)* | Translation of capstone UML class diagrams into modular, executable Python OOP classes across all four subsystems. | Python OOP, Encapsulation, UML Architecture, Mermaid Diagrams | [Watch Video](https://youtu.be/DQiKX4fOofI?is=h-DeqQ0h0I1E1lw5) |
| **`Homeworkassignment002`** *(Home Task 2)* | Event-driven real-time video stream pipeline simulating an automated conveyor-belt optical sorter. | ABCs, Inheritance, Polymorphism, Operator Overloading (`\|`), Iterators, Generators, OpenCV, YOLO | [Watch Video](https://youtu.be/k51r7ukfHzA?is=P5BkhNf_qACyAhTH) |
| **`Homeworkassignment003`** *(Home Task 3)* | Portable web API and database access layer for managing waste scan history and dashboard statistics. | Flask REST API, MySQL 8, Repository Pattern, SQL Transactions, CRUD UI | [Watch Video](https://youtu.be/Y_iwMYPAa_g?is=d5bWIP5ctaQV5dNj) |
| **`Homeworkassignment004`** *(Home Task 4)* | Subsystem-specific custom exception hierarchies, safe HTTP error handlers, and automated unit testing. | Custom Exceptions, Exception Chaining, Dependency Injection, Pytest (15 tests) | [Watch Video](https://www.youtube.com/watch?v=XhRAf5f_Iio) |

---

## Detailed Branch Summaries

### 1. Final Capstone (`Capstone-Project`)
The complete, end-to-end **EcoSort AI** application. Users upload or photograph a waste item, which is validated and preprocessed (`Subsystem 1`), classified via a trained local **YOLO** model (`Subsystem 2`), matched against local **German bin rules** or evaluated by a vision-capable **LLM assistant** when confidence is low (`Subsystem 3`), and logged into a **SQLite** database with an interactive glassmorphism **Flask dashboard** (`Subsystem 4`).
* **Highlights:** Available as a ready-to-run Docker image (`prasadhule001/ecosort-ai:1.1`), includes role-based access control (*User*, *Municipality Worker*, *Administrator*), and features a 54-test automated suite.

### 2. Home Assignment 1 (`Homeworkassignment001`)
Establishes the foundational object-oriented architecture of the project. Translates the team's Mermaid UML class diagrams into 16 distinct Python classes (4 per member) with encapsulated attributes, getters/setters, and deterministic demonstration inference requiring zero external dependencies.

### 3. Home Assignment 2 (`Homeworkassignment002`)
Demonstrates advanced Python OOP and real-time data streaming on a simulated conveyor-belt video (`media/conveyor_demo.mp4`). Implements a lazy evaluation pipeline (`VideoEventStream` iterator + `processed_events()` generator) where processors inherit from an abstract base class (`StreamProcessor`) and are composed using the overloaded `|` operator.

### 4. Home Assignment 3 (`Homeworkassignment003`)
Focuses on backend persistence and API design using **Flask** and **MySQL**. Separates SQL queries from routing logic using a dedicated repository and service layer, supporting full CRUD operations (`/api/scans`), aggregated metrics (`/api/stats`), and transaction rollbacks.

### 5. Home Assignment 4 (`Homeworkassignment004`)
Hardens the four subsystems against runtime failures by introducing domain-specific exceptions (e.g., `EmptyImageError`, `InferenceError`, `LLMServiceError`) with exception chaining (`raise ... from error`) and safe JSON error responses. Verified by 15 fast, dependency-injected unit tests using `pytest` and Pillow in-memory fixtures.

---

## How to Switch Branches

To explore a specific milestone locally, clone the repository and check out the desired branch:

```bash
git clone <repository-url>
cd <repository-folder>

# List all available branches
git branch -a

# Switch to a specific branch (e.g., Capstone-Project, Homeworkassignment001,...)
git checkout <branch-name>
```

Each branch contains its own dedicated `README.md` with step-by-step installation, environment setup, and execution instructions.
