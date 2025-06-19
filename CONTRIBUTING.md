# Contributing to QnaOps

Thank you for considering contributing to **QnaOps**! We welcome all kinds of contributions to help improve this end-to-end DevOps showcase.

---

## 🧠 What You Can Contribute

* 💡 Feature suggestions
* 🐛 Bug reports
* 📦 Kubernetes or Ansible improvements
* 🧪 Test coverage or validation scripts
* 🖥️ CI/CD enhancements
* 📖 Documentation improvements

---

## 🛠 Prerequisites

* Familiarity with Git, GitHub, and PR workflows
* Working knowledge of Docker, Kubernetes, and optionally Jenkins + Ansible
* Tested your changes in a local Minikube environment

---

## 🚀 Getting Started

1. **Fork** the repository on GitHub.
2. **Clone** your fork locally:

   ```bash
   git clone https://github.com/your-username/QnaOps.git
   cd QnaOps
   ```
3. **Create a new branch** for your feature or fix:

   ```bash
   git checkout -b feat/your-feature-name
   ```
4. **Make and test your changes** locally.
5. **Commit your changes** using [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):

   ```bash
   git commit -m "feat(observability): add dashboard export script"
   ```
6. **Push your branch**:

   ```bash
   git push origin feat/your-feature-name
   ```
7. **Open a Pull Request** targeting `main`.

---

## 📏 Guidelines

* 📌 Keep PRs focused and atomic.
* 📄 Document any changes made to scripts, pipelines, or infrastructure.
* 🔒 Never hard-code secrets. Use Ansible Vault or environment configs.
* 🔍 Add comments where logic or configuration isn't obvious.

---

## 🧪 Testing Your Changes

Before submitting a PR:

* ✅ Deploy your stack using `minikube-start.sh` and `kubectl apply`.
* ✅ Run Ansible playbooks with your `vault_pass.txt`.
* ✅ Use `load-test.sh`, `hpa-usage.sh`, and other utility scripts to validate behavior.

---

## 🙏 Thanks

Your contribution helps improve this project for future developers exploring CI/CD, Kubernetes, and cloud-native automation.

If you have questions, feel free to open an issue or start a discussion.

Made with 💙 by [@Peddinti-Sriram-Bharadwaj](https://github.com/Peddinti-Sriram-Bharadwaj)
