#!/usr/bin/env python
"""
PhotoShow Build Script
======================

This script compiles PhotoShow into a standalone executable with
Cloudinary credentials EMBEDDED at build time (not at runtime).

Usage:
    # Option 1: Interactive input (you're prompted for credentials)
    python scripts/build.py --interactive

    # Option 2: Pass via command-line arguments
    python scripts/build.py --cloud-name your_cloud_name --api-key your_api_key --api-secret your_secret

Why this approach?
    - Credentials are embedded at compile time
    - dist/PhotoShow can be copied anywhere without the repository
    - dist/PhotoShow works standalone on any machine
    - No need for .env file to be present after compilation
    - Users can't accidentally forget to copy .env
"""

import shutil
import subprocess
import sys
from argparse import ArgumentParser
from pathlib import Path


def get_credentials():
    """Get Cloudinary credentials from CLI args or interactive input."""
    parser = ArgumentParser(description="PhotoShow Build Script")
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Prompt for credentials interactively",
    )
    parser.add_argument("--cloud-name", help="Cloudinary cloud name")
    parser.add_argument("--api-key", help="Cloudinary API key")
    parser.add_argument("--api-secret", help="Cloudinary API secret")
    parser.add_argument(
        "--default-avatar-id", help="Default avatar public ID (optional)"
    )
    parser.add_argument("--default-avatar-url", help="Default avatar URL (optional)")

    args = parser.parse_args()

    credentials = {}

    # Try CLI args first
    if args.cloud_name:
        credentials["CLOUDINARY_CLOUD_NAME"] = args.cloud_name
    if args.api_key:
        credentials["CLOUDINARY_API_KEY"] = args.api_key
    if args.api_secret:
        credentials["CLOUDINARY_API_SECRET"] = args.api_secret
    if args.default_avatar_id:
        credentials["DEFAULT_AVATAR_PUBLIC_ID"] = args.default_avatar_id
    if args.default_avatar_url:
        credentials["DEFAULT_AVATAR_URL"] = args.default_avatar_url

    # If interactive or missing credentials, prompt user
    if args.interactive or not all(
        k in credentials
        for k in [
            "CLOUDINARY_CLOUD_NAME",
            "CLOUDINARY_API_KEY",
            "CLOUDINARY_API_SECRET",
        ]
    ):
        print("\n" + "=" * 70)
        print("📸 PhotoShow Build Configuration")
        print("=" * 70)
        print("\nEnter your Cloudinary credentials (from cloudinary.com/console):\n")

        if "CLOUDINARY_CLOUD_NAME" not in credentials:
            credentials["CLOUDINARY_CLOUD_NAME"] = input("  Cloud Name: ").strip()
        if "CLOUDINARY_API_KEY" not in credentials:
            credentials["CLOUDINARY_API_KEY"] = input("  API Key: ").strip()
        if "CLOUDINARY_API_SECRET" not in credentials:
            credentials["CLOUDINARY_API_SECRET"] = input("  API Secret: ").strip()

        print("\nOptional - Default Avatar (leave blank to skip):\n")
        if "DEFAULT_AVATAR_PUBLIC_ID" not in credentials:
            default_id = input("  Default Avatar Public ID: ").strip()
            if default_id:
                credentials["DEFAULT_AVATAR_PUBLIC_ID"] = default_id
        if "DEFAULT_AVATAR_URL" not in credentials:
            default_url = input("  Default Avatar URL: ").strip()
            if default_url:
                credentials["DEFAULT_AVATAR_URL"] = default_url

        print()

    # Validate required credentials
    required = [
        "CLOUDINARY_CLOUD_NAME",
        "CLOUDINARY_API_KEY",
        "CLOUDINARY_API_SECRET",
    ]
    missing = [k for k in required if k not in credentials or not credentials[k]]
    if missing:
        print("\n❌ ERROR: Missing required Cloudinary credentials:")
        for key in missing:
            print(f"   - {key}")
        print("\nProvide them via:")
        print("   1. Command-line args: python scripts/build.py --cloud-name value")
        print("   2. Interactive mode: python scripts/build.py --interactive")
        sys.exit(1)

    return credentials


def create_env_file(credentials: dict, project_root: Path) -> Path:
    """Create .env file with embedded credentials."""
    env_path = project_root / ".env"

    env_content = f"""CLOUDINARY_CLOUD_NAME={credentials.get('CLOUDINARY_CLOUD_NAME', '')}
CLOUDINARY_API_KEY={credentials.get('CLOUDINARY_API_KEY', '')}
CLOUDINARY_API_SECRET={credentials.get('CLOUDINARY_API_SECRET', '')}

DEFAULT_AVATAR_PUBLIC_ID={credentials.get('DEFAULT_AVATAR_PUBLIC_ID', '')}
DEFAULT_AVATAR_URL={credentials.get('DEFAULT_AVATAR_URL', '')}
"""

    with open(env_path, "w") as f:
        f.write(env_content)

    print(f"✅ Created .env file: {env_path}")
    return env_path


def verify_env_file(env_path: Path) -> bool:
    """Verify .env file has required credentials."""
    if not env_path.exists():
        print(f"❌ ERROR: .env file not found at {env_path}")
        return False

    with open(env_path) as f:
        content = f.read()

    required = ["CLOUDINARY_CLOUD_NAME", "CLOUDINARY_API_KEY", "CLOUDINARY_API_SECRET"]
    missing = [k for k in required if k not in content or f"{k}=" not in content]

    if missing:
        print(f"❌ ERROR: .env file missing required credentials: {missing}")
        return False

    print("✅ .env file verified with credentials")
    return True


def run_pyinstaller(spec_file: Path, project_root: Path) -> bool:
    """Run PyInstaller with the spec file."""
    print("\n" + "=" * 70)
    print("🔨 Building executable with PyInstaller...")
    print("=" * 70)

    # Clean up old build artifacts (dist/ and build/ folders) to ensure a fresh build
    dist_dir = project_root / "dist"
    build_dir = project_root / "build"

    if dist_dir.exists():
        print(f"🧹 Removing old dist folder: {dist_dir}")
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        print(f"🧹 Removing old build folder: {build_dir}")
        shutil.rmtree(build_dir)

    cmd = ["pyinstaller", str(spec_file), "--clean", "--noconfirm"]

    try:
        result = subprocess.run(cmd, check=True, cwd=str(project_root))
        return result.returncode == 0
    except FileNotFoundError:
        print("\n❌ ERROR: PyInstaller not found!")
        print("Install it with: pip install pyinstaller")
        return False
    except subprocess.CalledProcessError as e:
        print(f"\n❌ ERROR: PyInstaller failed with code {e.returncode}")
        return False


def verify_dist_build(project_root: Path) -> bool:
    """Verify the dist folder was built correctly."""
    dist_folder = project_root / "dist" / "PhotoShow"
    exe_file = dist_folder / "PhotoShow.exe"
    env_file = dist_folder / ".env"

    print("\n" + "=" * 70)
    print("🔍 Verifying build output...")
    print("=" * 70)

    if not dist_folder.exists():
        print("❌ ERROR: dist/PhotoShow folder not created")
        return False
    print(f"✅ dist/PhotoShow folder exists: {dist_folder}")

    if not exe_file.exists():
        print("❌ ERROR: PhotoShow.exe not found")
        return False
    print(f"✅ PhotoShow.exe exists: {exe_file}")

    if not env_file.exists():
        print("❌ ERROR: .env not bundled in dist folder")
        return False
    print(f"✅ .env bundled in dist: {env_file}")

    # Verify .env has credentials
    with open(env_file) as f:
        env_content = f.read()

    required = [
        "CLOUDINARY_CLOUD_NAME=",
        "CLOUDINARY_API_KEY=",
        "CLOUDINARY_API_SECRET=",
    ]
    if not all(k in env_content for k in required):
        print("❌ ERROR: .env in dist is missing credentials")
        return False
    print("✅ .env contains all Cloudinary credentials")

    return True


def main():
    """Main build workflow."""
    project_root = Path(__file__).parent.parent.resolve()

    print("\n" + "=" * 70)
    print("📦 PhotoShow Build Script")
    print("=" * 70)
    print(f"\nProject root: {project_root}")

    # Step 1: Get credentials
    print("\nStep 1️⃣  Reading Cloudinary credentials...")
    credentials = get_credentials()
    print(f"✅ Got credentials for cloud: {credentials['CLOUDINARY_CLOUD_NAME']}")

    # Step 2: Create .env file
    print("\nStep 2️⃣  Creating .env file with embedded credentials...")
    env_file = create_env_file(credentials, project_root)
    if not verify_env_file(env_file):
        sys.exit(1)

    # Step 3: Run PyInstaller
    print("\nStep 3️⃣  Compiling with PyInstaller...")
    spec_file = project_root / "PhotoShow.spec"
    if not spec_file.exists():
        print(f"❌ ERROR: {spec_file} not found")
        sys.exit(1)

    if not run_pyinstaller(spec_file, project_root):
        sys.exit(1)

    # Step 4: Copy .env next to PhotoShow.exe
    # PyInstaller 6.x places datas inside _internal/, but main.py loads .env
    # from Path(sys.executable).parent (i.e. dist/PhotoShow/.env), so we copy
    # it manually to guarantee the correct location regardless of PyInstaller version.
    print("\nStep 4️⃣  Copying .env to dist/PhotoShow/...")
    dist_dir = project_root / "dist" / "PhotoShow"
    if not dist_dir.exists():
        print("❌ ERROR: dist/PhotoShow not found after PyInstaller")
        sys.exit(1)
    env_src = project_root / ".env"
    env_dst = dist_dir / ".env"
    shutil.copy2(env_src, env_dst)
    print(f"✅ .env copied to: {env_dst}")

    # Step 5: Verify build
    print("\nStep 5️⃣  Verifying build...")
    if not verify_dist_build(project_root):
        sys.exit(1)

    # Success!
    print("\n" + "=" * 70)
    print("✨ BUILD SUCCESSFUL!")
    print("=" * 70)
    print("""
📍 Executable location: dist/PhotoShow/PhotoShow.exe

🚀 Next steps:

   1. Copy the dist/PhotoShow folder to your Desktop or anywhere:
      copy -r dist/PhotoShow C:\\Users\\User\\Desktop\\PhotoShow_Portable

   2. You can now DELETE the entire repository folder if you want

   3. Run PhotoShow from the copied folder:
      C:\\Users\\User\\Desktop\\PhotoShow_Portable\\PhotoShow.exe

✅ The executable is SELF-CONTAINED:
   ✓ All Python runtime bundled (_internal folder)
   ✓ All assets bundled (app/assets)
   ✓ All seed data bundled (app/files)
   ✓ Cloudinary credentials bundled (.env)

   NO dependencies on the repository!

⚠️  SECURITY NOTE:
   The compiled .exe contains your Cloudinary credentials.
   Keep dist/PhotoShow secure and don't share publicly.
""")


if __name__ == "__main__":
    main()
