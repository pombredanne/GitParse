Post Commit hook utility
========================

This module graps the git log from your last commit and uses it to:

	1. Update GUS items
	2. Create a code review
	
To use this, create the following post_commit in your .git/hooks directory
of your repository and make executable

	#!/usr/bin/env python
	
	from git.PostCommit import PostCommit
	
	pc = PostCommit()
	pc.commit()
	
You can also utilize a the webservice to do the updates asynchronously

	#!/usr/bin/env python
	
	from git.PostCommit import PostCommit
	
	pc = PostCommit()
	pc.remote()
		

It provides a module that parses the last commit log and gives you

Author:
	- name
	- email
	
Comment:
	- title (parses first line as title)
	- overview (remaining lines)
	- annotations (as a dictionary.  @key value in comments)
	
Changes:
	- list (Files that were modified/added/deleted in the commit)
	
Patch:
	- diff (A unified diff file that can be used to create code reviews)
