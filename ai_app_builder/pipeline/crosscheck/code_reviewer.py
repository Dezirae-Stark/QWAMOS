#!/usr/bin/env python3
"""
QWAMOS Phase 9: Code Crosscheck Reviewer

Each AI reviews the others' code for:
- Security vulnerabilities
- Code quality issues
- Logic errors
- Performance problems

@module code_reviewer
@version 1.0.0
"""

import logging
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger('CodeReviewer')


class ReviewType(Enum):
    """Type of code review"""
    SECURITY = "security"
    QUALITY = "quality"
    PERFORMANCE = "performance"
    ARCHITECTURE = "architecture"


@dataclass
class CodeIssue:
    """Single code issue found during review"""
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    type: str
    file: str
    line: int
    description: str
    suggestion: str


class CodeCrosscheckReviewer:
    """
    Cross-check reviewer - each AI reviews others' work

    Process:
    1. Claude generates code
    2. Kali GPT reviews for security
    3. ChatGPT reviews for quality
    4. Issues aggregated and resolved
    """

    def __init__(self, kali_gpt, claude, chatgpt):
        self.kali_gpt = kali_gpt
        self.claude = claude
        self.chatgpt = chatgpt

    async def crosscheck_review(
        self,
        code: Dict[str, str],
        author_ai: str
    ) -> List[CodeIssue]:
        """
        Perform crosscheck review by other AIs

        Args:
            code: Code to review
            author_ai: Which AI wrote the code

        Returns:
            List of issues found
        """
        issues = []

        # Security review by Kali GPT (if not author)
        if author_ai != "kali_gpt":
            logger.info("Kali GPT security review...")
            kali_issues = await self.kali_gpt.review_for_security(code)
            issues.extend(kali_issues)

        # Quality review by ChatGPT (if not author)
        if author_ai != "chatgpt":
            logger.info("ChatGPT quality review...")
            chatgpt_issues = await self.chatgpt.review_for_quality(code)
            issues.extend(chatgpt_issues)

        # Architecture review by Claude (if not author)
        if author_ai != "claude":
            logger.info("Claude architecture review...")
            claude_issues = await self.claude.review_for_architecture(code)
            issues.extend(claude_issues)

        # Filter and prioritize issues
        critical_issues = [i for i in issues if i.severity == "CRITICAL"]

        if critical_issues:
            logger.warning(f"Found {len(critical_issues)} CRITICAL issues")

        return issues

    def categorize_issues(self, issues: List[CodeIssue]) -> Dict[str, List[CodeIssue]]:
        """Categorize issues by severity"""
        categories = {
            'CRITICAL': [],
            'HIGH': [],
            'MEDIUM': [],
            'LOW': []
        }

        for issue in issues:
            categories[issue.severity].append(issue)

        return categories
