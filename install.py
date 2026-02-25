#!/usr/bin/env python3
import sys
import os
import subprocess
import shutil
import hashlib
import tempfile

try:
    import termios
    import tty
except ImportError:
    termios = None
    tty = None

class Installer:
    class Colors:
        HEADER = "\033[95m"
        BLUE = "\033[94m"
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        RED = "\033[91m"
        ENDC = "\033[0m"
        BOLD = "\033[1m"

    REPO_URL = "https://github.com/RengeOS/NiriWM-Edition.git"

    def __init__(self):
        self.default_config_dir = os.path.expanduser("~/.config/")
        self.source_dir = None
        self.config_dir = self.default_config_dir
        self.aur_helper = None
        self.dry_run = False
        self.protected_files = [
            "user_settings.json",
            "colors.scss",
            "preview-colors.scss",
        ]
        self.auto_confirm_overwrite = False
        self.auto_confirm_delete = False

    def run(self):
        self.print_header("Welcome to NiriWM Edition Dotfiles -*-RengeOS-*-")

        command_exists = shutil.which("house-overlay-update") is not None

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                self.clone_repo(self.REPO_URL, temp_dir)
                self.source_dir = temp_dir
                self.update_installed_command_if_needed()

                print("1: Full Installation")
                print(f"{self.Colors.RED}2: Uninstall{self.Colors.ENDC}")
                print("q: Quit")
                options = ["1", "2", "q"]
                choice = self.get_user_choice("Select an option: ", options)

                if not command_exists and choice in ["1", "2"]:
                    self.install_as_command()

                if choice == "1":
                    self.full_install()
                elif choice == "2":
                    self.uninstall()
                elif choice == "q":
                    print("Quitting.")
        except Exception as e:
            print(f"{self.Colors.RED}An unexpected error occurred: {e}{self.Colors.ENDC}")
            sys.exit(1)
        finally:
            print("\nTemporary files have been cleaned up.")

    def clone_repo(self, repo_url, dest_dir):
        if not shutil.which("git"):
            print(f"{self.Colors.RED}Git command not found. Please install Git.{self.Colors.ENDC}")
            sys.exit(1)

        print(f"Cloning '{repo_url}' into a temporary directory...")
        result = subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, dest_dir],
            capture_output=True, text=True, check=False
        )

        if result.returncode != 0:
            print(f"{self.Colors.RED}Error cloning repository: {result.stderr}{self.Colors.ENDC}")
            sys.exit(1)

    def run_command(self, cmd, **kwargs):
        if self.dry_run:
            print(f"{self.Colors.YELLOW}[DRY RUN] Would execute: {' '.join(cmd)}{self.Colors.ENDC}")
            return subprocess.CompletedProcess(cmd, 0)
        else:
            try:
                return subprocess.run(cmd, check=True, **kwargs)
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                print(f"{self.Colors.RED}Error executing command: {e}{self.Colors.ENDC}")
                return None

    def print_header(self, title):
        print(f"\n{self.Colors.HEADER}{self.Colors.BOLD}{'=' * 50}{self.Colors.ENDC}")
        print(f" {self.Colors.HEADER}{self.Colors.BOLD}{title}{self.Colors.ENDC}")
        print(f"{self.Colors.HEADER}{self.Colors.BOLD}{'=' * 50}{self.Colors.ENDC}")

    def get_user_choice(self, prompt, options):
        if termios and tty:
            try:
                print(f"{self.Colors.YELLOW}{prompt}{self.Colors.ENDC}", end="", flush=True)
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(fd)
                    while True:
                        char = sys.stdin.read(1)
                        if char.lower() in options:
                            print(char)
                            return char.lower()
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            except termios.error:
                pass
        
        while True:
            option = input(f"{self.Colors.YELLOW}{prompt}{self.Colors.ENDC}").lower()
            if option in options:
                return option
            print(f"{self.Colors.RED}Invalid input.{self.Colors.ENDC}")

    def get_file_hash(self, file_path):
        hasher = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                hasher.update(f.read())
            return hasher.hexdigest()
        except IOError:
            return None

    def check_aur_helper(self):
        self.print_header("Checking for AUR Helper")
        if shutil.which("paru"):
            self.aur_helper = "paru"
        elif shutil.which("yay"):
            self.aur_helper = "yay"

        if self.aur_helper:
            print(f"{self.Colors.GREEN}Found AUR helper: {self.aur_helper}{self.Colors.ENDC}")
            return True

        print(f"{self.Colors.YELLOW}Neither paru nor yay found. Attempting to install yay...{self.Colors.ENDC}")
        if self.install_yay():
            if shutil.which("yay"):
                self.aur_helper = "yay"
                return True

        print(f"{self.Colors.RED}Failed to find or install an AUR helper.{self.Colors.ENDC}")
        return False

    def install_yay(self):
        print("Installing base-devel and git...")
        if not self.run_command(["sudo", "pacman", "-S", "--needed", "--noconfirm", "git", "base-devel"]):
            return False

        yay_bin_dir = "yay-bin"
        if os.path.exists(yay_bin_dir):
            shutil.rmtree(yay_bin_dir)

        print("Cloning yay from the AUR...")
        if not self.run_command(["git", "clone", "https://aur.archlinux.org/yay-bin.git"]):
            return False

        try:
            os.chdir(yay_bin_dir)
            print("Running makepkg to build and install yay...")
            result = self.run_command(["makepkg", "-si", "--noconfirm"])
            os.chdir("..")
            shutil.rmtree(yay_bin_dir)
            return result is not None
        except Exception as e:
            print(f"{self.Colors.RED}An error occurred during yay installation: {e}{self.Colors.ENDC}")
            if os.getcwd().endswith(yay_bin_dir):
                os.chdir("..")
            return False

    def install_dependencies(self):
        self.print_header("Installing Dependencies")
        
        choice = self.get_user_choice("Do you want to automatically install dependencies? (y/n): ", ["y", "n"])
        if choice == "n":
            print("Skipping dependency installation.")
            return

        packages = [ 
            "ttf-material-symbols-variable-git", "wlogout",
            "matugen", "hyprlax", "gnome-bluetooth-3.0", "adw-gtk-theme",
            "playerctl", "nerd-fonts", "starship", "fish",
            "python-pywalfox", "gnome-themes-extra", "fuzzel", "cliphist",
            "xwayland-satellite", "xdg-desktop-portal", "xdg-desktop-portal-gtk",
            "xdg-desktop-portal-gnome", "xorg-xwayland",
            "qt5-base", "qt6-base", "gtk3", "gtk4", "brightnessctl", "nautilus",
            "slurp", "networkmanager", "libnotify",
            "libpulse", "niri", "waybar", "base-devel", "kitty", "ttf-jetbrains-mono-nerd",
            "pamixer", "ttf-nerd-fonts-symbols", "wlsunset", "hyprlock", "swaync", "pavucontrol"
        ]

        print(f"Attempting to install dependencies using {self.aur_helper}...")
        result = self.run_command([self.aur_helper, "-S", "--noconfirm"] + packages)
        
        if result is None or (hasattr(result, "returncode") and result.returncode != 0):
             print(f"{self.Colors.RED}Failed to install some packages. You may need to install them manually.{self.Colors.ENDC}")


        self.print_header("Installing Local PKGBUILD Packages (Requires Sudo)")

        print("\nInstalling Polkit Gnome Switch from source...")
        polkit_dir = os.path.join(self.source_dir, "PKGBUILD", "Polkit-Gnome-Switch")
        self.run_command(["makepkg", "-si", "--noconfirm"], cwd=polkit_dir)


    def final_setup(self):
        self.print_header("Final Setup")

        # Starship setup
        default_starship = os.path.join(self.source_dir, "Home-Overlay", "defaults", "starship.toml")
        starship_dest = os.path.expanduser("~/.config/starship.toml")
        if not os.path.exists(starship_dest):
            print("Copying default starship.toml...")
            os.makedirs(os.path.dirname(starship_dest), exist_ok=True)
            shutil.copyfile(default_starship, starship_dest)
            
        # Wallpaper setup
        default_wp = os.path.join(self.source_dir, "Home-Overlay", "defaults", "default-wallpaper.jpg")
        wp_dir = os.path.expanduser("~/Pictures/Wallpapers")
        if self.dry_run:
            wp_dir = os.path.join(self.config_dir, "Pictures/Wallpapers")
        
        os.makedirs(wp_dir, exist_ok=True)
        wp_dest = os.path.join(wp_dir, "default-wallpaper.jpg")
        
        if not os.path.exists(wp_dest):
            print("Copying default wallpaper...")
            shutil.copyfile(default_wp, wp_dest)

        print(f"{self.Colors.GREEN}Default wallpaper placed in {wp_dir}{self.Colors.ENDC}")

        # Matugen

        print("\nGenerating initial color scheme with Matugen...")
        if shutil.which("matugen"):
            if self.run_command(["matugen", "image", wp_dest]):
                print(f"{self.Colors.GREEN}Initial color scheme generated.{self.Colors.ENDC}")
        else:
            print(f"{self.Colors.RED}Matugen not found. Skipping color generation.{self.Colors.ENDC}")
            

        # Extension setup
        ext_source = os.path.join(self.source_dir, "Extensions", "VSCodium", "hyprluna-theme-1.0.2.vsix")
        if self.dry_run:
            ext_source = os.path.join(self.source_dir, "Home-Overlay", "Extensions", "VSCodium", "hyprluna-theme-1.0.2.vsix")

        for editor in ["vscodium", "code"]:
            if shutil.which(editor):
                if self.get_user_choice(f"\nInstall hyprluna theme for {editor}? (y/n): ", ["y", "n"]) == "y":
                    self.run_command([editor, "--install-extension", ext_source])

        if shutil.which("house-overlay-update") is None:
            self.install_as_command()

    def full_install(self):
        self.print_header("Starting Full Installation")

        # Distro check implies Arch now, so just check file presence
        if not os.path.exists("/etc/arch-release"):
             print(f"{self.Colors.RED}This script is optimized for Arch based on Linux. Proceed with caution.{self.Colors.ENDC}")

        if not self.dry_run:
            if not self.check_aur_helper():
                return
            self.install_dependencies()
        
        # Copy Configs
        core_folders = ["niri", "matugen", "fish", "gtk-3.0", "gtk-4.0", "helix", "fuzzel", "kitty", "waybar", "wlogout", "swaync"]
        for folder in core_folders:
            source = os.path.join(self.source_dir, "Home-Overlay", folder)
            destination = os.path.join(self.config_dir, folder)
            
            if os.path.exists(destination):
                print(f"{self.Colors.YELLOW}Warning: '{destination}' already exists.{self.Colors.ENDC}")
                choice = self.get_user_choice("Backup (b), Overwrite (o), or Quit (q)? ", ["b", "o", "q"])
                if choice == "b":
                    shutil.move(destination, destination + "-backup")
                elif choice == "o":
                    shutil.rmtree(destination)
                elif choice == "q":
                    sys.exit(0)
            try:
                shutil.copytree(source, destination)
                print(f"{self.Colors.GREEN}Copied '{folder}'.{self.Colors.ENDC}")
            except Exception as e:
                print(f"{self.Colors.RED}Error copying '{folder}': {e}{self.Colors.ENDC}")

        # Copy Home folders (e.g. .icons)
        home_folders = [".icons"]
        for folder in home_folders:
            source = os.path.join(self.source_dir, "Home-Overlay", folder)
            destination = os.path.expanduser(os.path.join("~", folder))
            if os.path.exists(destination):
                 # Simple overwrite logic for icons to save space/time
                 shutil.rmtree(destination)
            try:
                shutil.copytree(source, destination)
            except Exception as e:
                print(f"{self.Colors.RED}Error copying '{folder}': {e}{self.Colors.ENDC}")

        # Run Scripts
        print("\nInstalling Deepin Icons...")
        icon_script_dir = os.path.join(self.source_dir, "Scripts-For-Installer", "install-deepin-icons-scripts")
        self.run_command(["bash", "./deepin-icons-installer.sh"], cwd=icon_script_dir)


        self.final_setup()
        print(f"\n{self.Colors.GREEN}Installation complete.{self.Colors.ENDC}")


    def install_as_command(self):
        self.print_header("Installing as Command")
        dest_dir = "/usr/local/bin"
        os.makedirs(dest_dir, exist_ok=True)
        dest_file = os.path.join(dest_dir, "house-overlay-update")
        
        try:
            self.run_command(["sudo", "cp", sys.argv[0], dest_file])
            self.run_command(["sudo", "chmod", "755", dest_file])
            print(f"{self.Colors.GREEN}Installed to {dest_file}{self.Colors.ENDC}")
        except Exception as e:
            print(f"{self.Colors.RED}Error installing command: {e}{self.Colors.ENDC}")

    def update_installed_command_if_needed(self):
        installed_path = "/usr/local/bin/house-overlay-update"
        if not os.path.exists(installed_path): return
        
        cloned_script = sys.argv[0]
        if os.path.basename(cloned_script) == "house-overlay-update":
            cloned_script = os.path.join(self.source_dir, "install.py")

        if self.get_file_hash(installed_path) != self.get_file_hash(cloned_script):
             print(f"{self.Colors.YELLOW}Updating command...{self.Colors.ENDC}")
             self.run_command(["sudo", "cp", cloned_script, installed_path])

    def uninstall(self):
        self.print_header("Uninstaller")
        print(f"{self.Colors.RED}WARNING: Removing configuration files.{self.Colors.ENDC}")
        
        if self.get_user_choice("Continue? (y/n): ", ["y", "n"]) == "n": return

        paths = [
            os.path.join(self.config_dir, "matugen"),
            os.path.join(self.config_dir, "fish"),
            os.path.join(self.config_dir, "kitty"),
            os.path.join(self.config_dir, "gtk-3.0"),
            os.path.join(self.config_dir, "gtk-4.0"),
            os.path.join(self.config_dir, "helix"),
            os.path.join(self.config_dir, "fuzzel"),
            os.path.join(self.config_dir, "niri"),
            os.path.join(self.config_dir, "waybar"),
            os.path.join(self.config_dir, "wlogout"),
            os.path.join(self.config_dir, "swaync"),
            "/usr/local/bin/house-overlay-update",
            os.path.expanduser("~/Pictures/Wallpapers/default-wallpaper.jpg"),
            os.path.expanduser("~/.config/starship.toml"),
            os.path.expanduser("~/.config/hypr/hyprlock.conf"),
            os.path.expanduser("~/.icons/")
        ]

        for path in paths:
            if os.path.exists(path):
                if self.dry_run:
                    print(f"[DRY RUN] Remove {path}")
                    continue
                try:
                    if os.path.isdir(path): shutil.rmtree(path)
                    else: 
                        if path.startswith("/usr/local"): self.run_command(["sudo", "rm", path])
                        else: os.remove(path)
                    print(f"Removed {path}")
                except Exception as e:
                    print(f"Error removing {path}: {e}")

        self.print_header("Uninstall Complete")
        print("Note: Dependencies were NOT removed to preserve system stability.")

if __name__ == "__main__":
    if os.geteuid() == 0:
        print("Please run as a regular user, not root.")
        sys.exit(1)

    installer = Installer()
    if len(sys.argv) > 1 and sys.argv[1] == "--uninstall":
        installer.uninstall()
    else:
        installer.run()
