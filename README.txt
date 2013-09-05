Post Commit hook utility
========================

This module graps the git log from your last commit and uses it to:

	1. Update GUS items
	2. Create a code review
	
To use this, create the following commit-msg and post-commit in your .git/hooks directory
of your repository and make executable

commit-msg:
    #!/usr/bin/env python
    import sys
    from git.Git import CommitMessage
    cm = CommitMessage()
    cm.validate(sys.argv[1])

post-commit:
	#!/usr/bin/env python
	
	from git.PostCommit import PostCommit
	
	pc = PostCommit()
	pc.commit()
	
You can also utilize a the webservice to do the updates asynchronously.
The web service is a django project in the internal git hub.  Just clone
git@git.soma.salesforce.com:/halifax/PostCommitService.git and fire it up.

	#!/usr/bin/env python
	
	from git.PostCommit import PostCommit
	
	pc = PostCommit()
	pc.remote()
	
The default server is localhost:8000.  If you want to specify a server

	#!/usr/bin/env python
	
	from git.PostCommit import PostCommit
	
	pc = PostCommit()
	pc.remote(server="my.remote.com:8000")

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
