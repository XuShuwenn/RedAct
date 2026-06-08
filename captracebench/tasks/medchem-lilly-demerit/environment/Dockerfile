FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -qq && apt-get install -y -qq libxrender1 libxft2 libxext6 && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir medchem==2.0.5 datamol==0.12.5

WORKDIR /root

COPY input.txt /root/input.txt

COPY skills /root/.claude/skills
COPY skills /root/.codex/skills
COPY skills /root/.opencode/skill
COPY skills /root/.agents/skills

RUN mkdir -p /logs/verifier /logs/agent /logs/artifacts