FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN pip install --no-cache-dir matchms==0.32.0

WORKDIR /root

COPY input.msp /root/input.msp

COPY skills /root/.claude/skills
COPY skills /root/.codex/skills
COPY skills /root/.opencode/skill
COPY skills /root/.agents/skills

RUN mkdir -p /logs/verifier /logs/agent /logs/artifacts