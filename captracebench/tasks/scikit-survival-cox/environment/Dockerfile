FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN pip install --no-cache-dir scikit-survival==0.27.0 pandas==2.2.2

WORKDIR /root

COPY input.csv /root/input.csv

COPY skills /root/.claude/skills
COPY skills /root/.codex/skills
COPY skills /root/.opencode/skill
COPY skills /root/.agents/skills

RUN mkdir -p /logs/verifier /logs/agent /logs/artifacts