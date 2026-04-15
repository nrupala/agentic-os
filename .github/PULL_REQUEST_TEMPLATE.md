name: Pull Request
description: Submit changes to the project
title: "[PR]: "
labels: ["triage"]
body:
  - type: markdown
    attributes:
      value: |
        ## Pull Request Checklist

        Please review and check all items:

  - type: checkboxes
    id: testing
    attributes:
      label: Testing
      options:
        - label: Tests added/updated
        - label: All tests pass locally
        - label: Tested on multiple platforms (if applicable)

  - type: checkboxes
    id: quality
    attributes:
      label: Code Quality
      options:
        - label: Code follows project style
        - label: No linting errors
        - label: Appropriate comments added
        - label: Docstrings updated (if applicable)

  - type: checkboxes
    id: documentation
    attributes:
      label: Documentation
      options:
        - label: README updated (if applicable)
        - label: Code comments added for complex logic
        - label: API documentation updated (if applicable)

  - type: checkboxes
    id: security
    attributes:
      label: Security
      options:
        - label: No secrets hardcoded
        - label: Security implications considered
        - label: Input validation added (if applicable)

  - type: textarea
    id: description
    attributes:
      label: Description
      description: Summary of changes
      placeholder: Briefly describe your changes
    validations:
      required: true

  - type: textarea
    id: motivation
    attributes:
      label: Motivation
      description: Why is this change needed?
      placeholder: Context behind the changes

  - type: textarea
    id: breaking
    attributes:
      label: Breaking Changes
      description: Any breaking changes?
      placeholder: List any breaking changes or "None"

  - type: textarea
    id: related
    attributes:
      label: Related Issues
      description: Link related issues
      placeholder: "Fixes #123, Related to #456"

  - type: textarea
    id: screenshot
    attributes:
      label: Screenshots/Logs
      description: Add screenshots or log output
      placeholder: Add any visual evidence if applicable
