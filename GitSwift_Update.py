import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
import git
from datetime import datetime
from github import Github
import json
import webbrowser

class RepoUpdateGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GitSwift Update Tool")
        self.root.geometry("450x350")  # Smaller height
        
        # Hide terminal window (Windows only)
        try:
            import win32gui
            import win32con
            hwnd = win32gui.GetForegroundWindow()
            win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
        except ImportError:
            pass  # win32gui not available
        
        # Set theme colors
        self.colors = {
            'bg': '#0d1117',            # Dark background
            'secondary_bg': '#161b22',   # Secondary background
            'text': '#c9d1d9',          # Text color
            'accent': '#238636',         # Green accent
            'input_bg': '#21262d',      # Input background
            'input_text': '#c9d1d9',    # Input text
            'button_bg': '#238636',     # Button background (green)
            'button_text': '#ffffff',    # Button text (white)
            'button_hover': '#2ea043',   # Button hover color
            'success': '#238636',        # Success color
            'error': '#f85149',         # Error color
            'border': '#30363d',        # Border color
            'title_bg': '#0d1117'       # Title bar background
        }
        
        # Configure root window
        self.root.configure(bg=self.colors['bg'])
        
        # Set title bar color (Windows only) - updated approach
        try:
            from ctypes import windll, byref, sizeof, c_int
            HWND = windll.user32.GetParent(self.root.winfo_id())
            
            # Define constants
            DWMWA_TITLEBAR_COLOR = 35
            DWMWA_TEXT_COLOR = 36
            DWMWA_BORDER_COLOR = 34
            
            # Set colors
            windll.dwmapi.DwmSetWindowAttribute(
                HWND, 
                DWMWA_TITLEBAR_COLOR,
                byref(c_int(0x0d1117)),  # Dark background
                sizeof(c_int)
            )
            windll.dwmapi.DwmSetWindowAttribute(
                HWND,
                DWMWA_TEXT_COLOR,
                byref(c_int(0xFFFFFF)),  # White text
                sizeof(c_int)
            )
            windll.dwmapi.DwmSetWindowAttribute(
                HWND,
                DWMWA_BORDER_COLOR,
                byref(c_int(0x0d1117)),  # Dark border
                sizeof(c_int)
            )
        except:
            pass
        
        # Configure styles
        self.style = ttk.Style()
        
        # Frame style
        self.style.configure(
            'Custom.TFrame',
            background=self.colors['bg']
        )
        
        # Label style
        self.style.configure(
            'Custom.TLabel',
            background=self.colors['bg'],
            foreground=self.colors['text'],
            font=('Segoe UI', 10)
        )
        
        # Button style
        self.style.configure(
            'Custom.TButton',
            background=self.colors['button_bg'],
            foreground=self.colors['button_text'],
            font=('Segoe UI', 10, 'bold'),  # Made font bold
            padding=8,                       # Increased padding
            relief='raised',                 # Added relief
            borderwidth=2                    # Added border
        )
        
        # Add hover effect for buttons
        self.style.map('Custom.TButton',
            background=[('active', self.colors['button_hover'])],
            relief=[('pressed', 'sunken')]
        )
        
        # Entry style
        self.style.configure(
            'Custom.TEntry',
            fieldbackground=self.colors['input_bg'],
            foreground=self.colors['text'],
            insertcolor=self.colors['text'],
            borderwidth=1,
            relief='solid'
        )
        
        # LabelFrame style
        self.style.configure(
            'Custom.TLabelframe',
            background=self.colors['bg'],
            foreground=self.colors['text']
        )
        self.style.configure(
            'Custom.TLabelframe.Label',
            background=self.colors['bg'],
            foreground=self.colors['text'],
            font=('Segoe UI', 10, 'bold')
        )
        
        # Combobox style
        self.style.configure(
            'Custom.TCombobox',
            fieldbackground=self.colors['input_bg'],
            background=self.colors['button_bg'],
            foreground=self.colors['text'],
            selectbackground=self.colors['accent'],
            selectforeground=self.colors['text'],
            arrowcolor=self.colors['text']
        )
        
        # Checkbutton style
        self.style.configure(
            'Custom.TCheckbutton',
            background=self.colors['bg'],
            foreground=self.colors['text']
        )
        
        # Load saved repositories and GitHub token
        self.load_config()
        
        self.create_widgets()

    def load_config(self):
        """Load configuration including recent repositories and GitHub token"""
        try:
            if os.path.exists('repo_config.json'):
                with open('repo_config.json', 'r') as f:
                    config = json.load(f)
                    self.github_token = config.get('github_token', '')
                    self.recent_repos = config.get('recent_repos', [])
            else:
                self.github_token = ''
                self.recent_repos = []
        except Exception as e:
            print(f"Error loading config: {e}")
            self.github_token = ''
            self.recent_repos = []

    def save_config(self):
        """Save configuration including recent repositories and GitHub token"""
        try:
            config = {
                'github_token': self.github_token,
                'recent_repos': self.recent_repos
            }
            with open('repo_config.json', 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Error saving config: {e}")

    def create_widgets(self):
        # Create main container with padding
        self.main_frame = ttk.Frame(self.root, style='Custom.TFrame', padding="5")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Repository Section
        repo_frame = ttk.LabelFrame(
            self.main_frame, 
            text="Repository", 
            padding="2",
            style='Custom.TLabelframe'
        )
        repo_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))

        # Combined Path Entry and Dropdown
        self.repo_path = tk.StringVar()
        self.path_combo = ttk.Combobox(
            repo_frame,
            textvariable=self.repo_path,
            values=self.recent_repos,
            width=35,  # Reduced width
            style='Custom.TCombobox'
        )
        self.path_combo.grid(row=0, column=0, padx=2, pady=2, sticky="ew")
        
        # Buttons Frame
        btn_frame = tk.Frame(repo_frame, bg=self.colors['bg'])
        btn_frame.grid(row=0, column=1, padx=5)
        
        # Button style configuration
        button_config = {
            'bg': '#2ea043',          # GitHub green
            'fg': '#ffffff',          # White text
            'font': ('Segoe UI', 8),  # Smaller font
            'relief': 'raised',
            'borderwidth': 1,
            'padx': 5,    # Minimal padding
            'pady': 2,    # Minimal padding
            'cursor': 'hand2'
        }

        # Setup button config (blue)
        setup_button_config = {
            **button_config,
            'bg': '#1f6feb',          # GitHub blue
            'activebackground': '#388bfd'  # Lighter blue on hover
        }

        tk.Button(
            btn_frame, 
            text="Browse",
            command=self.browse_repo,
            **button_config
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            btn_frame,
            text="Initialize Git",
            command=self.init_repo,
            **button_config
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            btn_frame,
            text="Open in GitHub",
            command=self.open_github,
            **button_config
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            btn_frame,
            text="Setup Repository",
            command=self.setup_repository,
            **setup_button_config
        ).pack(side=tk.LEFT, padx=2)

        # Add hover effects
        def on_enter(e):
            if e.widget['bg'] == '#2ea043':  # Green buttons
                e.widget['background'] = '#3fb950'
            else:  # Blue button
                e.widget['background'] = '#388bfd'

        def on_leave(e):
            if e.widget['bg'] == '#3fb950':  # Green buttons
                e.widget['background'] = '#2ea043'
            else:  # Blue button
                e.widget['background'] = '#1f6feb'

        # Bind hover events
        for button in btn_frame.winfo_children():
            button.bind("<Enter>", on_enter)
            button.bind("<Leave>", on_leave)

        # Update combobox behavior
        def on_path_change(event=None):
            path = self.repo_path.get()
            if path and path not in self.recent_repos:
                self.recent_repos.insert(0, path)
                if len(self.recent_repos) > 5:  # Keep only 5 most recent
                    self.recent_repos.pop()
                self.path_combo['values'] = self.recent_repos
                self.save_config()

        self.path_combo.bind('<<ComboboxSelected>>', on_path_change)
        self.path_combo.bind('<Return>', on_path_change)

        # Text input configuration with different background colors
        text_config_base = {
            'fg': '#ffffff',
            'bg': '#21262d',
            'insertbackground': '#ffffff',
            'selectbackground': '#2ea043',
            'selectforeground': '#ffffff',
            'relief': 'solid',
            'borderwidth': 1,
            'font': ('Segoe UI', 8)  # Smaller font
        }

        # Different background colors for different priority levels
        high_priority_config = {
            **text_config_base,
            'bg': '#21262d'          # Darker shade for high priority
        }

        normal_priority_config = {
            **text_config_base,
            'bg': '#2d333b'          # Medium shade for normal priority
        }

        future_config = {
            **text_config_base,
            'bg': '#373e47'          # Lighter shade for future enhancements
        }

        # Update Information Frame
        info_frame = ttk.LabelFrame(
            self.main_frame,
            text="Update Information",
            padding="5",
            style='Custom.TLabelframe'
        )
        info_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 20))

        # Description
        ttk.Label(
            info_frame,
            text="Description:",
            style='Custom.TLabel'
        ).grid(row=0, column=0, sticky="nw", padx=5, pady=5)
        
        self.update_desc = tk.Text(info_frame, height=1, width=35, **high_priority_config)
        self.update_desc.grid(row=0, column=1, padx=2, pady=1)

        # Known Issues
        ttk.Label(
            info_frame,
            text="Known Issues:",
            style='Custom.TLabel'
        ).grid(row=1, column=0, sticky="nw", padx=5, pady=5)
        
        self.known_issues = tk.Text(info_frame, height=1, width=35, **normal_priority_config)
        self.known_issues.grid(row=1, column=1, padx=2, pady=1)

        # Todo Items Section with three separate fields
        todo_frame = ttk.LabelFrame(
            info_frame,
            text="Todo Items",
            padding="2",
            style='Custom.TLabelframe'
        )
        todo_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=2)

        # High Priority Todo
        ttk.Label(
            todo_frame,
            text="High Priority:",
            style='Custom.TLabel'
        ).grid(row=0, column=0, sticky="nw", padx=5, pady=5)
        
        self.high_priority_todo = tk.Text(todo_frame, height=1, width=35, **high_priority_config)
        self.high_priority_todo.grid(row=0, column=1, padx=2, pady=1)

        # Normal Priority Todo
        ttk.Label(
            todo_frame,
            text="Normal Priority:",
            style='Custom.TLabel'
        ).grid(row=1, column=0, sticky="nw", padx=5, pady=5)
        
        self.normal_priority_todo = tk.Text(todo_frame, height=1, width=35, **normal_priority_config)
        self.normal_priority_todo.grid(row=1, column=1, padx=2, pady=1)

        # Future Enhancements
        ttk.Label(
            todo_frame,
            text="Future Enhancements:",
            style='Custom.TLabel'
        ).grid(row=2, column=0, sticky="nw", padx=5, pady=5)
        
        self.future_enhancements = tk.Text(todo_frame, height=1, width=35, **future_config)
        self.future_enhancements.grid(row=2, column=1, padx=2, pady=1)

        # GitHub Integration Frame
        github_frame = ttk.LabelFrame(
            self.main_frame,
            text="GitHub Integration",
            padding="2",
            style='Custom.TLabelframe'
        )
        github_frame.grid(row=3, column=0, sticky="ew", pady=5)

        # Token entry and save button in one row
        token_label = ttk.Label(github_frame, text="Token:", style='Custom.TLabel')
        token_label.grid(row=0, column=0, padx=2, pady=2)
        
        self.token_var = tk.StringVar(value=self.github_token)
        token_entry = ttk.Entry(
            github_frame,
            textvariable=self.token_var,
            show="*",
            width=30,
            style='Custom.TEntry'
        )
        token_entry.grid(row=0, column=1, padx=2, pady=2)
        
        save_token_btn = tk.Button(
            github_frame,
            text="Save Token",
            command=self.save_token,
            **button_config
        )
        save_token_btn.grid(row=0, column=2, padx=5, pady=2)

        # Create GitHub Issue checkbox and Update Repository button in same row
        bottom_frame = tk.Frame(github_frame, bg=self.colors['bg'])
        bottom_frame.grid(row=1, column=0, columnspan=3, sticky='ew', pady=5)
        
        self.create_issue_var = tk.BooleanVar(value=False)
        issue_check = ttk.Checkbutton(
            bottom_frame,
            text="Create GitHub Issue",
            variable=self.create_issue_var,
            style='Custom.TCheckbutton'
        )
        issue_check.pack(side=tk.LEFT, padx=5)

        update_btn = tk.Button(
            bottom_frame,
            text="Update Repository",
            command=self.update_repository,
            **button_config
        )
        update_btn.pack(side=tk.RIGHT, padx=5)

        # Status Label
        self.status_var = tk.StringVar()
        status_label = ttk.Label(
            self.main_frame,
            textvariable=self.status_var,
            style='Custom.TLabel',
            wraplength=800
        )
        status_label.grid(row=5, column=0, columnspan=2, pady=10)

        # Adjust frame padding
        for frame in [repo_frame, info_frame, todo_frame, github_frame]:
            frame.configure(padding="1")

        # Adjust vertical spacing
        repo_frame.grid(pady=1)
        info_frame.grid(pady=1)
        todo_frame.grid(pady=1)
        github_frame.grid(pady=1)

    def init_repo(self):
        """Initialize a new git repository"""
        path = self.repo_path.get()
        if not path:
            messagebox.showerror("Error", "Please select a directory first")
            return
            
        try:
            git.Repo.init(path)
            messagebox.showinfo("Success", "Repository initialized successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize repository: {str(e)}")

    def open_github(self):
        """Open repository in GitHub"""
        try:
            repo = git.Repo(self.repo_path.get())
            url = repo.remotes.origin.url
            if url.endswith('.git'):
                url = url[:-4]
            webbrowser.open(url)
        except Exception as e:
            messagebox.showerror("Error", "Could not open GitHub page. Make sure this is a GitHub repository.")

    def browse_repo(self):
        """Browse for repository directory"""
        path = filedialog.askdirectory()
        if path:
            self.repo_path.set(path)
            if path not in self.recent_repos:
                self.recent_repos.insert(0, path)
                if len(self.recent_repos) > 5:  # Keep only 5 most recent
                    self.recent_repos.pop()
                self.save_config()

    def save_token(self):
        """Save GitHub token"""
        token = self.token_var.get()
        if token:
            self.save_github_token(token)
            self.github_token = token
            messagebox.showinfo("Success", "GitHub token saved successfully!")
        else:
            messagebox.showerror("Error", "Please enter a GitHub token")

    def create_github_issue(self, repo_path, update_desc, known_issues, todo_items):
        """Create a GitHub issue for the update"""
        try:
            if not self.github_token:
                raise ValueError("GitHub token not configured")

            g = Github(self.github_token)
            
            # Extract repository owner and name from remote URL
            repo = git.Repo(repo_path)
            remote_url = repo.remotes.origin.url
            owner_repo = remote_url.split('.git')[0].split('github.com/')[-1]
            
            # Get GitHub repository
            github_repo = g.get_repo(owner_repo)
            
            # Get current date for the title
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            # Create a more descriptive title from the description
            title = f"Update ({current_date}): {update_desc[:50]}..." if len(update_desc) > 50 else f"Update ({current_date}): {update_desc}"

            # Build the issue body with conditional sections
            body = f"""# Repository Update - {current_date}

## Description
{update_desc}
"""

            # Only add Known Issues section if there are any
            if known_issues.strip():
                body += f"""
## Known Issues
{known_issues}
"""

            # Add Todo sections only if they contain content
            high_priority = self.high_priority_todo.get("1.0", tk.END).strip()
            normal_priority = self.normal_priority_todo.get("1.0", tk.END).strip()
            future_enhancements = self.future_enhancements.get("1.0", tk.END).strip()

            if any([high_priority, normal_priority, future_enhancements]):
                body += "\n## Todo Items"
                
                if high_priority:
                    body += f"""
### 🔴 High Priority
{high_priority}
"""

                if normal_priority:
                    body += f"""
### 🟡 Normal Priority
{normal_priority}
"""

                if future_enhancements:
                    body += f"""
### 🔵 Future Enhancements
{future_enhancements}
"""

            # Add footer
            body += """
---
*This issue was automatically created by the Repository Update Tool*"""

            # Determine labels based on content
            labels = ['update']
            if known_issues.strip():
                labels.append('has-issues')
            if high_priority:
                labels.append('high-priority')
            if future_enhancements:
                labels.append('enhancement')

            # Create the issue with appropriate labels
            github_repo.create_issue(title=title, body=body, labels=labels)
            
            self.status_var.set("Repository updated and GitHub issue created successfully!")
            return True
            
        except Exception as e:
            messagebox.showerror("GitHub Error", f"Failed to create issue: {str(e)}")
            self.status_var.set("Repository updated but failed to create GitHub issue")
            return False

    def update_repository(self):
        repo_path = self.repo_path.get()
        update_desc = self.update_desc.get("1.0", tk.END).strip()
        known_issues = self.known_issues.get("1.0", tk.END).strip()
        
        # Get content from all todo fields
        high_priority = self.high_priority_todo.get("1.0", tk.END).strip()
        normal_priority = self.normal_priority_todo.get("1.0", tk.END).strip()
        future_enhancements = self.future_enhancements.get("1.0", tk.END).strip()

        # Combine todo items with proper formatting
        todo_items = f"""## High Priority
{high_priority}

## Normal Priority
{normal_priority}

## Future Enhancements
{future_enhancements}"""

        if not repo_path or not update_desc:
            messagebox.showerror("Error", "Please provide repository path and update description")
            return

        try:
            self.status_var.set("Updating repository...")
            self.root.update()

            # Change to repository directory
            os.chdir(repo_path)
            current_date = datetime.now().strftime("%Y-%m-%d")

            # Update README.md
            self.update_readme(update_desc, current_date)

            # Update CHANGELOG.md
            self.update_changelog(update_desc, current_date)

            # Create UPDATE_NOTES.md
            self.create_update_notes(update_desc, known_issues, todo_items, current_date)

            # Git operations
            repo = git.Repo(repo_path)
            repo.index.add(['README.md', 'CHANGELOG.md', 'UPDATE_NOTES.md'])
            commit_message = f"update({current_date}): {update_desc}\n\n- Updated documentation\n- Added changelog entry\n- Created update notes"
            repo.index.commit(commit_message)

            if self.create_issue_var.get():
                if self.create_github_issue(repo_path, update_desc, known_issues, todo_items):
                    self.status_var.set("Repository updated and GitHub issue created!")
                else:
                    self.status_var.set("Repository updated but failed to create GitHub issue")

            self.status_var.set("Repository updated successfully!")
            messagebox.showinfo("Success", "Repository has been updated successfully!")

        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def update_readme(self, update_desc, current_date):
        if not os.path.exists('README.md'):
            with open('README.md', 'w') as f:
                f.write(f"# {os.path.basename(os.getcwd())}\n\n## Current Status\n🟢 Active Development\n")

        with open('README.md', 'r+') as f:
            content = f.read()
            if "### Latest Updates" not in content:
                f.write(f"\n### Latest Updates ({current_date})\n- {update_desc}\n")
            else:
                # Insert new update at the top of the updates section
                new_content = content.replace("### Latest Updates", f"### Latest Updates ({current_date})\n- {update_desc}\n")
                f.seek(0)
                f.write(new_content)
                f.truncate()

    def update_changelog(self, update_desc, current_date):
        if not os.path.exists('CHANGELOG.md'):
            with open('CHANGELOG.md', 'w') as f:
                f.write("# Changelog\n\n")

        with open('CHANGELOG.md', 'r+') as f:
            content = f.read()
            f.seek(0)
            f.write(f"## [{current_date}]\n### Added\n- {update_desc}\n\n{content}")

    def create_update_notes(self, update_desc, known_issues, todo_items, current_date):
        with open('UPDATE_NOTES.md', 'w') as f:
            f.write(f"""# Update Notes ({current_date})

## Changes Made
- {update_desc}

## Known Issues
{known_issues if known_issues else '- [ ] No known issues reported'}

## Todo
{todo_items if todo_items else '- [ ] No todo items added'}

## Testing Notes
- [ ] Add testing requirements/results

## Dependencies
- List any new dependencies added

## Migration Steps
1. Pull latest changes
2. [Add any necessary migration steps]

## Rollback Plan
1. [Document how to rollback these changes if needed]
""")

    def setup_repository(self):
        """Set up repository with proper structure and .gitignore"""
        repo_path = self.repo_path.get()
        if not repo_path:
            messagebox.showerror("Error", "Please select a repository path first")
            return

        # Create .gitignore if it doesn't exist
        gitignore_path = os.path.join(repo_path, '.gitignore')
        if not os.path.exists(gitignore_path):
            with open(gitignore_path, 'w') as f:
                f.write("""# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Local configuration
*.ini
*.cfg
config.json
github_config.json

# Logs
*.log
""")

        # Handle README (convert .txt to .md if needed)
        readme_txt_path = os.path.join(repo_path, 'README.txt')
        readme_md_path = os.path.join(repo_path, 'README.md')
        
        # If both exist, merge into .md and remove .txt
        if os.path.exists(readme_txt_path) and os.path.exists(readme_md_path):
            with open(readme_txt_path, 'r', encoding='utf-8') as txt_file:
                txt_content = txt_file.read()
            with open(readme_md_path, 'r', encoding='utf-8') as md_file:
                md_content = md_file.read()
            
            # Only append txt content if it's not already in md
            if txt_content not in md_content:
                with open(readme_md_path, 'a', encoding='utf-8') as md_file:
                    md_file.write(f"\n\n{txt_content}")
            
            # Remove the .txt file
            os.remove(readme_txt_path)
            
        # If only .txt exists, convert to .md
        elif os.path.exists(readme_txt_path):
            with open(readme_txt_path, 'r', encoding='utf-8') as txt_file:
                content = txt_file.read()
            with open(readme_md_path, 'w', encoding='utf-8') as md_file:
                md_file.write(f"# {os.path.basename(repo_path)}\n\n{content}")
            os.remove(readme_txt_path)
        
        # If no README exists, create .md
        elif not os.path.exists(readme_md_path):
            with open(readme_md_path, 'w', encoding='utf-8') as f:
                f.write(f"# {os.path.basename(repo_path)}\n\nRepository update tool\n")

        # Create or update ISSUES.md
        issues_path = os.path.join(repo_path, 'ISSUES.md')
        if not os.path.exists(issues_path):
            with open(issues_path, 'w', encoding='utf-8') as f:
                f.write("""# Known Issues

## Current Issues
- [ ] List current issues here

## Resolved Issues
- [x] Example resolved issue
""")

        # Create or update TODO.md
        todo_path = os.path.join(repo_path, 'TODO.md')
        if not os.path.exists(todo_path):
            with open(todo_path, 'w', encoding='utf-8') as f:
                f.write("""# Todo Items

## High Priority
- [ ] List high priority items here

## Normal Priority
- [ ] List normal priority items here

## Future Enhancements
- [ ] List future enhancements here
""")

        # Initialize git if needed
        try:
            repo = git.Repo(repo_path)
        except git.exc.InvalidGitRepositoryError:
            repo = git.Repo.init(repo_path)
        
        # Add remote if needed
        try:
            origin = repo.remote('origin')
        except ValueError:
            if messagebox.askyesno("Setup", "No remote repository found. Would you like to add one?"):
                remote_url = simpledialog.askstring("Remote URL", "Enter your GitHub repository URL:")
                if remote_url:
                    repo.create_remote('origin', remote_url)

        messagebox.showinfo("Success", "Repository setup complete!")

if __name__ == "__main__":
    # Hide terminal in Windows
    try:
        import win32gui
        import win32con
        console_hwnd = win32gui.GetForegroundWindow()
        win32gui.ShowWindow(console_hwnd, win32con.SW_HIDE)
    except ImportError:
        pass  # win32gui not available

    root = tk.Tk()
    # Apply system theme
    try:
        from tkinter import ttk
        import sys
        if sys.platform.startswith('win'):
            root.tk.call('source', 'azure.tcl')
            root.tk.call('set_theme', 'dark')
    except:
        pass
    
    app = RepoUpdateGUI(root)
    root.mainloop() 