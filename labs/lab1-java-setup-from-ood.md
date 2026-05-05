---
sidebar_position: 1
image: /img/labs/web/lab1.png
---

# 1 Introduction

Welcome to CS 3100! In this lab, you'll set up your Java development environment and get familiar with the tools we'll use throughout the course.

Getting your development environment working right now is essential so that you can focus on completing assignments and labs later on. To receive credit for this lab:

**Option 1: Successful Setup**

   - Complete all steps, resulting in a passing build (`./gradlew build` succeeds)
   - All tests pass
   - Push your completed work to GitHub

You'll see 2/2 in Pawtograder after submitting your lab if everything is working.

**Option 2: Incomplete Setup (Partial Credit)**

If you're unable to get everything working despite your best efforts:

   - Submit a `REFLECTION.md` that documents:
      - What steps you completed successfully
      - Where you got stuck and what error messages you encountered
      - What resources you tried (documentation, office hours, discussion forum, etc.)
      - What troubleshooting steps you attempted

You'll see 0/2 in Pawtograder after submitting your lab if everything is not working. A TA will review your reflection and give you credit if you made a good faith effort to complete the lab. A TA is also likely to reach out to you to insist that you meet with them in order to get your environment working.

We understand that environment setup can be frustrating, especially across different operating systems. The goal is to get you unstuck quickly — **come to office hours** if you're having trouble! If you have tips to share with other students to complete the lab, please share them on the course discussion board in Pawtograder.

## Learning Objectives

By the end of this lab, you will be able to:

- Explain what a build system does and why we use Gradle
- Install and configure Java 21 (Temurin)
- Open and build a Gradle project in VS Code
- Run tests using JUnit 5
- Run code style checkers on your project
- Check for linter errors on your own machine
- Use Git to commit and push changes to GitHub

# 2 Prerequisites

Before starting, ensure you have:

- [ ] A GitHub account (create one free at [github.com](https://github.com) if needed)
- [ ] git installed on your computer
- [ ] VS Code installed

For help with git installation, see the [CS 2100 setup instructions](https://neu-pdi.github.io/cs2100-public-resources/setup/#git-installation). If you do not have VS Code on your computer, simply install it by [downloading from here](https://code.visualstudio.com/). Further instructions for VS Code setup are included later in this lab.

## 2.1: Set Up Pawtograder and GitHub

Pawtograder is our course platform for assignments, grading, and collaboration. Before you can work on assignments, you need to connect your accounts.

For detailed instructions with screenshots, see the [Pawtograder Student Guide](https://docs.pawtograder.com/students/intro).

### 2.1.1 Quick Setup Steps

1. **Log in to Pawtograder** at [pawtograder.com](https://app.pawtograder.com) using your Northeastern credentials (click "Continue with Microsoft")
2. **Connect your GitHub account** — when prompted, click "Sign in with GitHub" and authorize Pawtograder
3. **Accept the organization invitation** — click "Open GitHub Organization Invitation" and accept using your GitHub account

> 💡 **Already have a GitHub account?** Use your existing account! This keeps all your coursework visible on your profile if you choose to make repositories public later.

> 🔄 **Already have Pawtograder linked to GitHub from CS 2100?** You'll still need to complete the steps above to enroll in the CS 3100 GitHub organization in Pawtograder (skipping step 2).

> ⚠️ **Course not showing up?** Enrollments sync automatically every hour. If you just registered, wait an hour and try again. If it still doesn't appear, contact your instructor.

## 2.2 Install Java 21 (Temurin)

We'll use Eclipse Temurin, a free, open-source distribution of Java.

> ⚠️ **IMPORTANT: You MUST use Java 21, not Java 25!**
>
> Even though Java 25 is newer, **do not install it**. Our build tools (Gradle 8 and, in particular, [the Pitest plugin](https://github.com/szpak/gradle-pitest-plugin/issues/380)) do not yet support Java 25. If you install Java 25, your builds (including in VS Code) will fail with cryptic errors along the lines of "Unsupported class file major version 69". It may be possible to configure a local development environment to use Java 25, but we do not support it.
>
> If you already have Java 25 installed, see the [Troubleshooting](#troubleshooting) section for how to switch to Java 21 (particularly important for Mac users).


### 2.2.1 Download the Installer

1. Go to the Adoptium download page: https://adoptium.net/temurin/releases/?version=21
2. Select your operating system:

   - **macOS**: Choose `.pkg` installer (use **aarch64** for Apple Silicon Macs, **x64** for Intel Macs)
   - **Windows**: Choose `.msi` installer (**x64** for most computers)
   - **Linux**: Choose `.tar.gz` or use your distribution's package manager

### 2.2.2 Run the Installer

#### macOS

1. Open the downloaded `.pkg` file
2. Follow the installation wizard
3. Click through the prompts and enter your password when asked

#### Windows

1. Open the downloaded `.msi` file
2. Follow the installation wizard
3. **Important:** On the "Custom Setup" screen, make sure these options are enabled:

   - ✅ "Set JAVA_HOME variable"
   - ✅ "Add to PATH"

#### Linux
For Ubuntu/Debian, you can also install via terminal:
```bash
sudo apt update
sudo apt install temurin-21-jdk
```

# 3 Organizing projects on your machine

We recommend that you create a folder on your computer that will contain all the projects for this class (e.g. a folder called `CS3100`). While it is not required, it is recommended for ease-of-use that you do not have spaces in the folder name.

**Note**: Please do not put this folder at a place where it is being backed up by some other program (e.g. OneDrive, dropbox, Google Drive, etc.). This often creates problems when one program (e.g. your IDE like VS Code) is changing things inside the folder while the backup program is also working there.

## 3.1 Basic terminal commands

First we review some basic commands that can be used to navigate folders and run programs without a GUI or an IDE. This skill will simplify many operations later on (compared to fighting the idiosyncracies of an IDE).

### 3.1.1 What to use

- Linux/Mac: use the terminal. Click on the search icon on the top right and type "terminal". 

- Windows: If you have installed Git correctly on your computer, you should have "Git Bash" installed. Click on the Windows button and search for "Git Bash". 

### 3.1.2 Essential Commands Reference

Here's your survival guide to terminal commands:

| Command | What It Does | Example |
|---------|-------------|---------|
| `pwd` | **P**rint **W**orking **D**irectory - shows where you are | `pwd` → `/Users/yourname/cs3100/sp26-lab3-your-username` |
| `ls` | **L**i**s**t files in current directory | `ls` → shows files and folders |
| `ls -la` | List ALL files (including hidden) with details | `ls -la` → shows `.git`, permissions, dates |
| `cd <path>` | **C**hange **D**irectory | `cd src/main/java` |
| `cd ..` | Go up one directory level | `cd ..` → from `/src/main` to `/src` |
| `cd ~` | Go to your home directory | `cd ~` → `/Users/yourname` |
| `cd -` | Go to previous directory | `cd -` → back where you were |
| `mkdir <name>` | Make a new directory | `mkdir my-folder` |
| `mv <src> <dst>` | Move or rename a file | `mv Wrong.Java Correct.java` |
| `rm <file>` | Remove a file (careful!) | `rm unwanted.txt` |
| `clear` | Clear the terminal screen | `clear` |

### 3.1.3 Navigation Challenge

Open a terminal.

1. Find out which folder you are currently in, using `pwd`.
2. Use the above commands suitably to navigate to the `CS3100` folder you created earlier.
3. Create a new folder called `temp` in it. Verify the results in Windows Explorer/Finder.
4. Navigate inside the `temp`.
5. Navigate back to where you started in Step 1.


# 4 Set Up VS Code

## 4.1 Connect Github account to your local Git installation

Before you can clone repositories from our course organization, you need to connect your local Git installation to GitHub with proper authorization. You should do this so that you would not need to enter your credentials each and every time you want to upload a change. This is done by creating "SSH keys". You can think of them as a pair of keys that identify you specifically. 

Please follow [the detailed instructions here](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent). **Be sure to follow the instructions for your operating system**.

In order to verify that your setup works correctly, open a terminal (on Mac/Linux) or Git Bash on Windows and type this:

``` ssh -T git@github.com ```

Don't change the email. The response should be a greeting with your GitHub username.

If you see this message, **SSH is configured correctly!** You can now clone repositories using SSH URLs (which start with `git@github.com:` instead of `https://`).

## 4.2 Clone the Lab Repository

Now you're ready to clone your lab repository. First, find your repository in Pawtograder:

1. Go to [Pawtograder](https://pawtograder.com)
2. Navigate to **Lab 1: Setup**
3. You'll see your repository link displayed on the assignment page
4. From Pawtograder, click on your repository link to open it on GitHub
5. Click the green **Code** button on GitHub
6. Select the **SSH** tab
7. Copy the SSH URL (it should look like `git@github.com:neu-cs3100/su26-lab1-<your-username>.git`)
8. Open a terminal.
9. Navigate within the terminal to the `CS3100` folder you created earlier, which is supposed to contain all the projects from this course.
10. Type `git clone XXXX` replacing XXXX with the SSH URL. Press Enter.
11. Verify that it created a folder for Lab 1, and inside it are the same files that you see in GitHub for Lab 1.
12. Open VS Code and select `File --> Open Folder` and navigate to the new folder the above step just created. Now the project will be open in VS Code.

**You will follow this process roughly for every assignment and lab**.

## 4.3 Install Suggested Extensions

When the project opens, VS Code will prompt you to install recommended extensions. **Click "Install"** when you see this prompt. *We* have curated this list of extensions for the workflow of this course, and therefore encourage you to trust and use them too.

If you don't see the prompt (or accidentally dismissed it):

1. Open the Command Palette (⌘+Shift+P on Mac, Ctrl+Shift+P on Windows/Linux)
2. Type "Extensions: Show Recommended Extensions" and select it
3. In the Extensions sidebar, you'll see a **Workspace Recommendations** section
4. Click the **Install Workspace Recommended Extensions** button (cloud icon with arrow) to install all recommended extensions at once

These extensions include the **Extension Pack for Java** (which provides Java language support, debugging, and testing) and **GitHub Pull Requests** (for easy commits and pushing).

After installing extensions, VS Code will automatically detect the Gradle project and start downloading dependencies.

## 4.4 Disable AI Features

For the first several assignments in this course, you must complete your work **without AI assistance** (see the [AI Policy in the syllabus](../syllabus#artificial-intelligence) for details). This isn't because AI tools aren't useful, but because you must first learn how to do the following things effectively:

1. **The ability to review what AI produces** — you can only catch AI mistakes if you understand the code well enough to have written it yourself
2. **The knowledge of what to ask** — effective prompting requires understanding the problem space and knowing what's possible


To disable AI features in VS Code:

1. Open VS Code Settings:
   - **Mac**: Press `⌘+,` (Command + comma)
   - **Windows/Linux**: Press `Ctrl+,`
2. In the search bar at the top, type: `chat.disableAIFeatures`
3. Check the box next to **"Chat: Disable AI Features"**

Alternatively, click this link to go directly to the setting: [vscode://settings/chat.disableAIFeatures](vscode://settings/chat.disableAIFeatures)

This disables GitHub Copilot, inline suggestions, and other AI-powered features. Later in the semester, we'll re-enable these tools and learn how to use them effectively — but first, let's build the skills to understand what they produce!

## 4.5 Verify Java Setup

After the project opens and extensions are installed, verify that VS Code is properly configured:

1. Look at the **bottom-left corner** of the VS Code window
2. You should see **"Java: Ready"** (with a checkmark icon)
   - If you see "Java: Loading" — wait a moment for it to finish
   - If you see "Java: Error" or nothing — see the [Troubleshooting](#troubleshooting) section
3. This indicator confirms that VS Code has found Java 21 and is ready to build your project


## 4.6 The Build System

Before we compile, let's understand what we're working with.

When you write Java code, you need to **compile** it (translate human-readable `.java` files into machine-executable `.class` files). But real projects need much more than just compilation:

- **Dependency management**: Your project uses external libraries (like JUnit for testing). Someone needs to download those libraries and make them available to your code.
- **Testing**: Running tests, generating reports, and failing the build if tests don't pass.
- **Code quality**: Running linters, formatters, and static analysis tools.
- **Packaging**: Bundling your code into a distributable format (like a `.jar` file).

A **build system** automates all of this. You describe *what* you want (your dependencies, your source files, your tests), and the build system figures out *how* to make it happen.

### Gradle: Our Build System

**Gradle** is one of the most popular build systems for Java (along with Maven and Ant). It's used by major projects including Android apps, Spring applications, and... this course!

Key Gradle files in this project:

- **`build.gradle`**: The main configuration file. Lists dependencies, plugins, and build settings.
- **`settings.gradle`**: Project name and multi-project configuration.
- **`gradlew` / `gradlew.bat`**: The "Gradle Wrapper" — a script that downloads and runs the correct version of Gradle automatically. This ensures everyone on the team uses the same Gradle version.

When you run `./gradlew compileJava`, you're telling Gradle: "Please compile my Java source files." Gradle then:

1. Downloads itself (if needed) via the wrapper
2. Reads `build.gradle` to understand the project
3. Downloads any missing dependencies
4. Compiles the code in the correct order
5. Reports any errors or warnings

> 💡 **Why `./gradlew` instead of just `gradle`?** The `./` runs the wrapper script in the current directory, which guarantees everyone uses Gradle 8.x for this project. If you had Gradle 7 or 9 installed globally, it will not work correctly.

# 5 Tasks

## 5.1 Compile the Project

On Windows, you can configure the integrated terminal in VS Code to open either PowerShell, CMD, or Git Bash.
We recommend [setting the default](https://stackoverflow.com/a/45899693/631051) to Git Bash.

   Open the integrated terminal (`⌘+ˋ` or `Ctrl+ˋ`) and run:

```bash
./gradlew compileJava
```

**On Windows** PowerShell (the DEFAULT if you have not changed it to Git Bash), use:
```cmd
.\gradlew.bat compileJava
```

### 5.1.1 Fixing Errors

For this class, you will find actual code in the `src` folder. Expand that folder on the project side window to reveal two other folders: `main` and `test` each with a folder called `java` in it. `main/java` is the *sources root*:  it is where the project expects all your code to be. Similarly `test/java` is the *test sources root*: it is where the project expects all your tests to be. You can open files in VS Code by double-clicking them. You will notice there are some building errors in one of the source code files.

   1. Hover your mouse over the error line and you should see a tooltip with an error message in it. Error messages are read better by clicking on the "Problems" tab at the bottom of the window.

   2. When you hover over an error in the source file, a window pops up which shows the error message along with some options at the bottom. Clicking on `Quick Fix...` provides suggestions by VS Code on how to correct this error (you can also get here by clicking on the yellow bulb that appears near the start of the line). **Read and understand each suggestion before clicking on one of them!**

   3. Correct the errors and warnings.

## 5.2 JUnit Testing
 
We will use the JUnit testing framework to write all our tests in this course. All tests must be placed in the *test sources root* (see above). For this lab, there is already
a file inside called `PersonTest.java`.

The import statements in `PersonTest.java` may produce an error because the project cannot locate JUnit files. If there are no errors, then that means gradle did its job and actually installed JUnit for you! Skip to the end of this section that talks about running the tests. If there is an error, hover on the error, and select "Quick Fix..." and then "Fix all errors". If that does not work, simply delete all the erroneous import statements, which will produce errors at several places in the file. Fix those errors as described in the previous section by accepting the suggestion to import the appropriate JUnit class.

### 5.2.1 Running the Tests

Run the tests by typing the following in the VS Code terminal: `./gradlew clean test` (Mac/Linux) or `.\gradlew.bat clean test` (Windows).

One of the tests will fail. **This is expected.** Note how it shows you the test failure. Fix this test according to the comment next to the failure, and verify that all tests pass.

## 5.3 Check and Fix Style

Run the style of your code by typing the following in the VS Code terminal: `./gradlew checkstyleMain` (Mac/Linux) or `.\gradlew.bat checkstyleMain` (Windows). Similarly you can check the style of your tests by replacing `checkstyleMain` with `checkstyleTest`.

## Alternative method to compile, test, check style...

`compileJava`, `test`, `clean`, `checkstyleMain` and `checkstyleTest` are all gradle commands. There is an alternative way to access them through the VS Code UI.

1. On the left side find the icon for Gradle (looks like an elephant). Click on it.
2. Drop-down `Tasks` to see various tasks classified into categories. For example, `compileJava`, `checkstyleMain` and `checkstyleTest` are in the "other" category. 
3. Hover on any task to reveal a triangle `Run` button. Click on it to run that task. This is equivalent to typing `./gradlew task-name` in the terminal.

# 6 Commit and Push

## 6.1 Git Refresher

**Git** is a *version control system* — software that tracks changes to your files over time. Think of it like "track changes" in a word processor, but far more powerful. With Git, you can:

- Go back to any previous version of your code
- See exactly what changed, when, and why
- Work on multiple features simultaneously without them interfering
- Collaborate with teammates without overwriting each other's work

**Key concepts:**

| Term | What it means |
|------|---------------|
| **Repository (repo)** | A folder whose history Git is tracking |
| **Commit** | A snapshot of your code at a point in time |
| **Staging** | Marking files to be included in the next commit |
| **Push** | Uploading your commits to a remote server (GitHub) |
| **Clone** | Downloading a repository from GitHub to your computer |

**The basic workflow:**
```
Working Directory → (git add) → Staging Area → (git commit) → Local Repository → (git push) → GitHub
```

1. You edit files in your **working directory**
2. You **stage** the changes you want to save (`git add`)
3. You **commit** those staged changes with a message (`git commit`)
4. You **push** your commits to GitHub (`git push`)

> 📚 **Want a deeper dive?** See the [CS 2100 Git introduction](https://neu-pdi.github.io/cs2100-public-resources/lecture-notes/next/l1-intro-python1#git) for a more thorough explanation with helpful diagrams and analogies.

**Note** Look below for a warning about using `git add .` even though the above page recommends it. 

## 6.2 Committing Your Work

Follow this workflow to submit your lab (and future assignments):

### 6.2.1 Check format

In the VS Code terminal, run `./gradlew spotlessApply`. Verify that there are no style errors.

### 6.2.2 Check build

Ensure that the project builds and runs without any errors: `./gradlew build`.

### 6.2.3 Commit and Push

#### From the terminal

This way is recommended for this lab, because it forces you to complete each step explicitly.

1. Open a terminal in VS Code or independently. Opening one in VS Code is better because you can see your project as well as the terminal within one window.
2. Navigate to the project folder (in this lab, that is your Lab 1 folder).
3. Type `git status`. This will show you which files have changed since the last time you committed, and which files are untracked (i.e. not backed up in Git). Since you only changed files within the `src/` folder, you should only have to pay attention to these files.
4. Navigate to the folder that contains your code. You may use `git status .` to check the status of only files within the current folder.
5. For each file that you wish to submit, type `git add <filename>`. If you use `git status` after this, you will see that the file(s) you added are shown in the staging area. **Do not use `git add .` which will add every file in the current folder to the staging area, including hidden files!** Instead add each file you want to, explicitly.
6. Once all the changed files are shown in the staging area, type `git commit -m <message>`. Replace `<message>` with a helpful text message that reminds you of what the changes are about.
7. To push the changes to Github (i.e. to submit on Pawtograder), type `git push origin main` (only `git push` will also work for now).

#### From VS Code

This way may be faster once you have many files to commit and push. These steps accomplish the same things as above, just handled by VS Code for convenience.

1. In VS Code with this project open, click the **Source Control** icon in the left sidebar (or press ⌃+Shift+G / Ctrl+Shift+G). You'll see a list of changed files.
2. Click the **+** next to each file (or click **+** next to "Changes" to stage all). This is equivalent to the `git add` steps above.
3. Type a commit message like "Complete Lab 1 tasks" and click the **✓ Commit** button. This is equivalent to the `git commit -m "Complete Lab 1 tasks"` step above.
4. Click **Sync Changes** to sync your commits to GitHub. This is equivalent to `git pull` followed by `git push`. The pulling is useful only when others are working in the same repository as you and have pushed changes that you do not have locally.

# 7 Complete the Reflection

Open `REFLECTION.md` and answer the questions about your experience with this lab.

Don't forget to commit and push your reflection!

## Submission Checklist

Before submitting, ensure:

- [ ] `./gradlew compileJava` passes with **0 warnings**
- [ ] `./gradlew test` passes with all tests passing
- [ ] You've fixed the error in the code
- [ ] You've fixed the error in the tests
- [ ] You've completed `REFLECTION.md`
- [ ] All changes are committed and pushed to GitHub

# 8 Troubleshooting

## 8.1 I installed Java 25 instead of Java 21

Java 25 is **not compatible** with our build tools. You need to install Java 21 and set it as your default.

### macOS

1. Install Java 21 (see instructions above)
2. List your installed Java versions:
   ```bash
   /usr/libexec/java_home -V
   ```
3. Set Java 21 as default by adding this to your `~/.zshrc` (or `~/.bashrc`):
   ```bash
   export JAVA_HOME=$(/usr/libexec/java_home -v 21)
   ```
4. Reload your shell: `source ~/.zshrc`
5. Verify: `java -version` should show version 21

If you see continued "Java Error" in VS Code, try clearing the Gradle cache:
```bash
./gradlew clean build --refresh-dependencies
```

In extreme cases, you can also try:
- Delete the `~/.gradle` directory
- Uninstall Java 25 (e.g. `rm -rf /Library/Java/JavaVirtualMachines/temurin-25.jdk`)
- Run the "Clean Java Language Server Workspace" command in VS Code
- Reboot your computer after completing these steps

#### Windows

1. Install Java 21 (see instructions above)
2. Open **System Properties** → **Advanced** → **Environment Variables**
3. Edit the `JAVA_HOME` variable to point to your Java 21 installation:
   - Typically: `C:\Program Files\Eclipse Adoptium\jdk-21.x.x-hotspot`
4. Edit the `Path` variable and move the Java 21 `bin` folder **above** any Java 25 entries
5. Open a **new** Command Prompt and verify: `java -version` should show version 21

#### Linux

1. Install Java 21 (see instructions above)
2. Use `update-alternatives` to switch versions:
   ```bash
   sudo update-alternatives --config java
   ```
3. Select the Java 21 option from the list
4. Verify: `java -version` should show version 21

## 8.2 "java: command not found"

Make sure you opened a **new** terminal after installing Java. If still not working:
- **macOS/Linux**: Add `export JAVA_HOME=$(/usr/libexec/java_home -v 21)` to your `~/.zshrc` or `~/.bashrc`
- **Windows**: Verify JAVA_HOME is set in System Environment Variables

## 8.3 VS Code doesn't recognize Java

1. Open Command Palette (⌘+Shift+P / Ctrl+Shift+P)
2. Type "Java: Configure Java Runtime"
3. Make sure Java 21 is detected and selected

## 8.4 Gradle build fails

Try clearing the Gradle cache:
```bash
./gradlew clean build --refresh-dependencies
```

## 8.5 SSH Authentication Issues

If you're having trouble with SSH authentication:

**"Permission denied (publickey)"**
- Make sure you've added your SSH key to GitHub (see [Add SSH Key to GitHub](#add-ssh-key-to-github))
- Test your connection: `ssh -T git@github.com`
- Make sure the SSH agent is running and has your key:
  ```bash
  ssh-add -l
  ```
  If your key isn't listed, add it:
  ```bash
  ssh-add ~/.ssh/id_ed25519
  ```

**SSH agent not running (Windows)**
- Open PowerShell as Administrator and run:
  ```powershell
  Get-Service ssh-agent | Set-Service -StartupType Automatic
  Start-Service ssh-agent
  ```

**SSH key passphrase prompts**
- If you set a passphrase on your SSH key, you'll be prompted to enter it when using the key
- On macOS, you can add your key to the keychain so you don't have to re-enter the passphrase:
  ```bash
  ssh-add --apple-use-keychain ~/.ssh/id_ed25519
  ```

**Still having SAML/authentication issues with HTTPS?**
- Switch to SSH authentication by following the [SSH setup instructions](#alternative-set-up-ssh-keys-recommended-to-avoid-saml-issues)
- If you already cloned with HTTPS, you can change to SSH:
  ```bash
  git remote set-url origin git@github.com:neu-cs3100/sp26-lab1-<your-username>.git
  ```

## 8.6 Resources

- [Java 21 Documentation](https://docs.oracle.com/en/java/javase/21/)
- [JUnit 5 User Guide](https://junit.org/junit5/docs/current/user-guide/)
- [VS Code Java Guide](https://code.visualstudio.com/docs/java/java-tutorial)
- [Course Website](https://neu-pdi.github.io/CS3100-Spring-2026/)
