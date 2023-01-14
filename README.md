# git-commit-script

## Usage
1. Download the script or clone the repository
2. Make the script executable by running `chmod +x commit.sh`
3. Run the script by executing the command `./commit.sh "Commit message"`

## Script functionality
- Prompts the user for the type of commit (e.g "fix", "add", "change", etc.)
- Automatically retrieves the current branch name as the task ID
- Capitalizes the first letter of the commit type
- Creates the commit message in the format of "$type: $commit_message #$task_id" if task id is matched otherwise "$type: $commit_message"
- Runs the git commit command with the modified message

## Note
- The script assumes that you are currently on the branch you want to create a commit for.
- This script is designed to work with branch naming conventions like "XP-1548-feature-branch-name". If your branch naming conventions are different, you may need to modify the script accordingly.

## License
This script is available under the MIT License. See the LICENSE file for more information.