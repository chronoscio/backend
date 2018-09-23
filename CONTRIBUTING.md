# How to contribute

Third-party patches are essential to ensure speedy development, and
we want to keep it as easy as possible to contribute changes. There
are a few guidelines that we need contributors to follow to ensure
consistent styling.

Note that this document is, in its current state, a draft and subject to change.

## Getting Started

- Consider joining our public [Discord server](https://discord.gg/QfRDgaY).
- Make sure you have a [GitHub account](https://github.com/signup/free).
- Check the [backend docs](./docs/).
- Submit a ticket on the issue tracker if one does not already exist.
  - Clearly describe the issue including steps to reproduce if it is a bug.
- Fork the repository on GitHub.

## Making Changes

- Create a topic branch from where you want to base your work.
  - This is usually the master branch.
  - Only target other branches if you are certain your fix must be on that
    branch.
  - Please avoid working directly on the `master` branch.
- Make commits of logical and atomic units.
- Check for unnecessary whitespace with `git diff --check` before committing.
- Make sure you have added the necessary tests in project/api/tests.py for your changes.

## Style guidelines

- Ensure all code follows [PEP 8](https://www.python.org/dev/peps/pep-0008/).
  The respository comes with [autopep8](https://github.com/hhatto/autopep8) to
  automate many parts of this. If using vscode autopep8 is preconfigured to use `.autopep8.py`
  to run the formatting remotely, and you can configure this to run on save. Otherwise, simply
  execute the script with the same arguments you would for the standard autopep8 binary.
- Make sure to use the `.pylint.py` binary to lint your code. This is automatically configured in
  vscode, otherwise, as before, call it with the same arguments you would use for the standard
  binary.
- Please use single quotes for strings, unless including single quotes in the string itself.
- Note that not all parts of the old code will follow these guidelines, which we are actively
  improving. Do not follow the conventions of surrounding code blocks if they do not conform
  to these guidelines.

## Submitting Changes

- Push your changes to a descriptive branch in your fork of the repository.
- Submit a pull request to the repository in the ChronoScio organization.
- Update your GitHub ticket to mark that you have submitted code and are ready
  for it to be reviewed
  - Include a link to the pull request in the ticket.
- After feedback has been given we expect responses within two weeks. After two
  weeks we may close the pull request if it isn't showing any activity.
