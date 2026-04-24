# Remote Integration Instructions

To link this local repository to a remote and **overwrite** the remote's existing history, execute the following:

1. **Add Remote Origin:**
   `git remote add origin <REMOTE_URL>`

2. **Force Push to Overwrite:**
   *Warning: This will delete all history on the remote 'main' branch.*
   `git push -u origin main --force`

3. **Verify Connection:**
   `git remote -v`
