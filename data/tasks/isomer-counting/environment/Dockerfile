FROM python:3.12-slim

RUN apt-get update -qq && apt-get install -y -qq curl && rm -rf /var/lib/apt/lists/*

WORKDIR /root

COPY input.txt /root/input.txt

COPY skills /root/.claude/skills
COPY skills /root/.codex/skills
COPY skills /root/.opencode/skill
COPY skills /root/.agents/skills

RUN mkdir -p /logs/verifier

CMD ["/bin/bash"]