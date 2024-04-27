# git-commit-script

## Installation

Run this command on terminal.

```shell
sudo curl https://raw.githubusercontent.com/bikal1000/git-commit-script/master/commit -o /usr/local/bin/commit && sudo chmod +x /usr/local/bin/commit
```

## Usage
* If your current branch name is `XP-1548-feature-branch-name`

```shell
commit

```
```shell
```bash
Select commit type:
1) Add
2) Change
3) Fix
4) Refactor
#? 1
Enter scope: my-feature
Enter commit message: Implemented new feature
```
```

```shell
# output
    git commit -m "Add(my-feature): Implemented new feature #XP-1548"
```

* If you want to push current branch to remote
```shell
commit -p

# becomes
git commit -m "Add(my-feature): Implemented new feature #XP-1548"
git push origin feature-branch-name
```


## Script functionality
- Prompts the user to select the commit type.
- Automatically retrieves the current branch name as the task ID
- Creates the commit message in the format of "$type($scope): $commit_message #$task_id" if task id is matched otherwise "$type($scope): $commit_message"
- Runs the git commit command with the modified message
- Push the current branch after commit 

## Note
- The script assumes that you are currently on the branch you want to create a commit for.
- This script is designed to work with branch naming conventions like "XP-1548-feature-branch-name". If your branch naming conventions are different, you may need to modify the script accordingly.

## License
This script is available under the MIT License. See the LICENSE file for more information.