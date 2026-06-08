"""Key Information Extractor Module"""

import string
import logging
from pathlib import Path
from typing import Optional

from .llm_client import LLMClient
from ..utils.config_loader import ConfigLoader
from ..prompts import KEY_INFO_EXTRACTION_PROMPT

logger = logging.getLogger(__name__)


class KeyInfoExtractor:
    """Extractor for identifying critical protected information in tasks and skills"""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        Initialize the extractor

        Args:
            llm_client: LLM client instance, created from config if not provided
        """
        self.llm_client = llm_client or LLMClient.from_config()
        self.prompt_template = KEY_INFO_EXTRACTION_PROMPT

    def extract(
        self,
        task_name: str,
        instruction: str,
        skill_docs: dict[str, str],
    ) -> dict[str, str]:
        """
        Extract critical information for a given task

        Args:
            task_name: Task name (short name, e.g., '3d-scan-calc')
            instruction: Task instruction text
            skill_docs: Dictionary of skill documents {skill_name: skill_content}

        Returns:
            Dictionary mapping {skill_name: key_info_text}
        """
        results = {}

        for skill_name, content in skill_docs.items():
            results[skill_name] = self.extract_skill(
                task_name=task_name,
                skill_name=skill_name,
                instruction=instruction,
                skill_doc=content,
            )

        return results

    def extract_skill(
        self,
        task_name: str,
        skill_name: str,
        instruction: str,
        skill_doc: str,
    ) -> str:
        """
        Extract critical information for one task-skill pair.

        The LLM sees exactly one skill name and its full SKILL.md document.

        Args:
            task_name: Task name (short name, e.g., '3d-scan-calc')
            skill_name: Skill directory/name (e.g., 'mesh-analysis')
            instruction: Task instruction text
            skill_doc: Full SKILL.md content

        Returns:
            Comma-separated key information text extracted from <key_info>.
        """
        skill_docs_text = f"\n\n## Skill: {skill_name}\n\n{skill_doc}\n"

        # Fill prompt template
        prompt = string.Template(self.prompt_template).substitute(
            TASK_INSTRUCTION=instruction,
            SKILL_DOCS=skill_docs_text,
        )

        # Call LLM
        logger.info(f"Extracting key info for task/skill: {task_name}/{skill_name}")
        response = self.llm_client.call(prompt)

        # Parse result
        key_info = self.llm_client.extract_tag_content(response, "key_info")

        if key_info is None:
            raise ValueError(f"No <key_info> tag found in LLM response for {task_name}/{skill_name}")

        return key_info.strip()

    def save_key_info(
        self,
        task_name: str,
        key_info_dict: dict[str, str],
        output_root: str = "protected_skills/captracebench",
    ) -> None:
        """
        Save critical information to files

        Args:
            task_name: Task name (short name)
            key_info_dict: Dictionary mapping {skill_name: key_info_text}
            output_root: Output root directory
        """
        for skill_name, key_info in key_info_dict.items():
            output_dir = Path(output_root) / task_name / skill_name
            output_dir.mkdir(parents=True, exist_ok=True)

            output_file = output_dir / "key_info.txt"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(key_info)

            logger.info(f"Saved key_info for {task_name}/{skill_name} -> {output_file}")

    def save_task_key_info(
        self,
        task_name: str,
        key_info_dict: dict[str, str],
        output_root: str = "protected_skills/captracebench",
        filename: str = "key_info_merged.txt",
    ) -> Path:
        """
        Save a task-level merged key information file.

        Args:
            task_name: Task name (short name)
            key_info_dict: Dictionary mapping {skill_name: key_info_text}
            output_root: Output root directory
            filename: Merged output filename under the task directory

        Returns:
            Path to the merged key information file
        """
        output_dir = Path(output_root) / task_name
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / filename
        sections = []
        for skill_name in sorted(key_info_dict):
            key_info = key_info_dict[skill_name].strip()
            if key_info:
                sections.append(f"## {skill_name}\n{key_info}")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n\n".join(sections).strip())
            f.write("\n" if sections else "")

        logger.info(f"Saved merged key_info for {task_name} -> {output_file}")
        return output_file

    def process_task(
        self,
        task_full_name: str,
        tasks_root: str = "data/tasks",
        output_root: str = "protected_skills/captracebench",
        save_merged: bool = True,
        merged_filename: str = "key_info_merged.txt",
    ) -> dict[str, str]:
        """
        Process a single task: read instruction and skill docs, extract and save critical info

        Args:
            task_full_name: Full task name (e.g., '3d-scan-calc__UPQPNRg')
            tasks_root: Tasks root directory
            output_root: Output root directory

        Returns:
            Dictionary mapping {skill_name: key_info_text}
        """
        # Parse task_name
        if "__" in task_full_name:
            task_name = task_full_name.split("__")[0]
        else:
            task_name = task_full_name

        task_dir = Path(tasks_root) / task_name

        if not task_dir.exists():
            raise FileNotFoundError(f"Task directory not found: {task_dir}")

        # Read instruction
        instruction_file = task_dir / "instruction.md"
        if not instruction_file.exists():
            raise FileNotFoundError(f"Instruction file not found: {instruction_file}")

        with open(instruction_file, "r", encoding="utf-8") as f:
            instruction = f.read()

        # Read all skill docs
        skills_dir = task_dir / "environment" / "skills"
        skill_docs = {}

        if skills_dir.exists():
            for skill_path in skills_dir.iterdir():
                if skill_path.is_dir():
                    skill_md = skill_path / "SKILL.md"
                    if skill_md.exists():
                        with open(skill_md, "r", encoding="utf-8") as f:
                            skill_docs[skill_path.name] = f.read()

        if not skill_docs:
            logger.warning(f"No skill docs found for {task_name}")
            return {}

        # Extract critical information
        key_info_dict = self.extract(task_name, instruction, skill_docs)

        # Save results
        self.save_key_info(task_name, key_info_dict, output_root)
        if save_merged:
            self.save_task_key_info(
                task_name=task_name,
                key_info_dict=key_info_dict,
                output_root=output_root,
                filename=merged_filename,
            )

        return key_info_dict
