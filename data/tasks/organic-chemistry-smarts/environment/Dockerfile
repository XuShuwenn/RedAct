FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN pip install --no-cache-dir rdkit==2026.3.1

WORKDIR /root

COPY input.txt /root/input.txt

COPY skills /root/.claude/skills
COPY skills /root/.codex/skills
COPY skills /root/.opencode/skill
COPY skills /root/.agents/skills

RUN mkdir -p /logs/verifier /logs/agent /logs/artifacts