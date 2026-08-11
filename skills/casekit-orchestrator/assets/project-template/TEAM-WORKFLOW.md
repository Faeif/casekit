# Team workflow — use this, not Git complexity

## One person sets up the project

1. Create the case workspace with CaseKit.
2. Put all source material in `inputs/`.
3. Create one **private** GitHub repository for this case and push this workspace to it.
4. Send only the case-repository link to teammates.

## Each teammate: first time only

```bash
git clone <CASE-REPOSITORY-URL>
cd <CASE-FOLDER>
python3 /path/to/casekit/install.py --scope project --project-root . --force
```

Open `<CASE-FOLDER>` as an Obsidian vault. Create your own draft folder, for example `00-INBOX/finance-may/`.

## Each teammate: every work session

```bash
git pull --rebase origin main
```

Work only inside your own `00-INBOX/<your-name>/` folder. Ask AI to write drafts there. When you want teammates to see the draft:

```bash
git add 00-INBOX/<your-name>
git commit -m "draft: finance first model"
git push origin main
```

If push is rejected, run the `git pull --rebase origin main` command again, then push again. Do not force-push and do not edit another person's draft folder.

## Integrator: after the team says “use this”

1. Pull the latest `main`.
2. Read the chosen draft in `00-INBOX/<name>/`.
3. Ask AI to promote only approved conclusions into the root official files.
4. Validate, then commit and push:

```bash
python3 /path/to/casekit/casekit.py validate . --strict
git add .
git commit -m "official: approve finance model"
git push origin main
```

Everyone then runs `git pull --rebase origin main` to receive the approved version.

## Simple rule

**Drafts go to your own INBOX folder. Approved work is promoted by the Integrator.**

Branches and pull requests are optional later. In Easy Team Mode, do not create a branch for every idea and never push to a friend's branch.
