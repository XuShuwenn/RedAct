FROM python:3.12-slim

RUN apt-get update -qq && apt-get install -y -qq curl && rm -rf /var/lib/apt/lists/*

WORKDIR /root

COPY input.csv /root/input.csv

COPY skills /root/.claude/skills
COPY skills /root/.codex/skills
COPY skills /root/.opencode/skill
COPY skills /root/.agents/skills

RUN mkdir -p /logs/verifier
RUN pip install --break-system-packages rdkit==2026.3.1 -q

CMD ["/bin/bash"]