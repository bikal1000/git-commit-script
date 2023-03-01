# git-commit-script

## Installation

Run this command on terminal.

```shell
sudo curl https://raw.githubusercontent.com/bikal1000/git-commit-script/master/commit -o /usr/local/bin/commit && sudo chmod +x /usr/local/bin/commit
```

## Usage
* If your current branch name is `XP-1548-feature-branch-name`

```shell
commit "issue type" "commit message"

# becomes
    git commit -m "Change: commit message #XP-1548"
```

* If your current branch name is `feature-branch-name`

```shell
commit "issue type" "commit message"

# becomes
    git commit -m "Change: commit message"
```

* If you want to push current branch to remote
```shell
commit "issue type" "commit message" -p

# becomes
git commit -m "Change: commit message #XP-1548"
git push origin feature-branch-name
```


## Script functionality
- Prompts the user for the type of commit (e.g "fix", "add", "change", etc.)
- Automatically retrieves the current branch name as the task ID
- Capitalizes the first letter of the commit type
- Creates the commit message in the format of "$type: $commit_message #$task_id" if task id is matched otherwise "$type: $commit_message"
- Runs the git commit command with the modified message
- Push the current branch after commit 

## Note
- The script assumes that you are currently on the branch you want to create a commit for.
- This script is designed to work with branch naming conventions like "XP-1548-feature-branch-name". If your branch naming conventions are different, you may need to modify the script accordingly.

## License
This script is available under the MIT License. See the LICENSE file for more information.