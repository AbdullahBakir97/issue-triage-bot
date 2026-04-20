"""Shared test fixtures for Issue Triage Bot."""

from __future__ import annotations

import pytest

from src.domain.entities import IssueContext


@pytest.fixture
def bug_issue() -> IssueContext:
    """A sample bug report issue context."""
    return IssueContext(
        issue_number=1,
        title="App crashes when clicking submit button",
        body=(
            "## Steps to reproduce\n"
            "1. Open the form\n"
            "2. Fill in all fields\n"
            "3. Click submit\n\n"
            "## Expected behavior\n"
            "Form should submit successfully\n\n"
            "## Actual behavior\n"
            "App crashes with error: TypeError: Cannot read property 'map' of undefined\n\n"
            "## Environment\n"
            "- OS: macOS 14.0\n"
            "- Browser: Chrome 120\n"
            "- Version: 2.1.0"
        ),
        author="testuser",
        repo_owner="testorg",
        repo_name="testrepo",
    )


@pytest.fixture
def feature_issue() -> IssueContext:
    """A sample feature request issue context."""
    return IssueContext(
        issue_number=2,
        title="Feature request: Add dark mode support",
        body=(
            "It would be nice to have a dark mode option.\n\n"
            "## Use case\n"
            "When working at night, the bright theme is hard on the eyes.\n\n"
            "## Proposed solution\n"
            "Add a toggle in settings to switch between light and dark themes."
        ),
        author="testuser",
        repo_owner="testorg",
        repo_name="testrepo",
    )


@pytest.fixture
def question_issue() -> IssueContext:
    """A sample question issue context."""
    return IssueContext(
        issue_number=3,
        title="How do I configure the API timeout?",
        body="I'm wondering how to change the default timeout for API requests. Help appreciated!",
        author="testuser",
        repo_owner="testorg",
        repo_name="testrepo",
    )


@pytest.fixture
def incomplete_bug_issue() -> IssueContext:
    """A bug report missing required sections."""
    return IssueContext(
        issue_number=4,
        title="Something is broken",
        body="The app doesn't work. Please fix.",
        author="testuser",
        repo_owner="testorg",
        repo_name="testrepo",
    )


@pytest.fixture
def security_issue() -> IssueContext:
    """A security vulnerability report."""
    return IssueContext(
        issue_number=5,
        title="Security vulnerability in authentication",
        body=(
            "There is a critical security vulnerability that allows unauthorized access.\n"
            "An attacker can exploit this to gain admin privileges and cause data loss."
        ),
        author="testuser",
        repo_owner="testorg",
        repo_name="testrepo",
    )
