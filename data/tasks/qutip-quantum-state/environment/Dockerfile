FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -qq && apt-get install -y -qq build-essential g++ && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir qutip==4.7.6 numpy==1.26.4

WORKDIR /root

COPY input.txt /root/input.txt

COPY skills /root/.claude/skills
COPY skills /root/.codex/skills
COPY skills /root/.opencode/skill
COPY skills /root/.agents/skills

RUN mkdir -p /logs/verifier /logs/agent /logs/artifacts