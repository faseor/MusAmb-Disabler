import shutil
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

# Project paths
ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
ASSETS_DIR = ROOT_DIR / "assets"
BUILD_DIR = ROOT_DIR / ".build"
DIST_DIR = ROOT_DIR / "dist"


def get_archive_name() -> str:
	info_xml = ASSETS_DIR / "fomod" / "info.xml"
	if not info_xml.exists():
		return "Mod_Release.zip"
	tree = ET.parse(info_xml)
	root = tree.getroot()
	name_el = root.find("Name")
	version_el = root.find("Version")
	name = name_el.text.strip().replace(" ", "_") if name_el is not None and name_el.text else "Mod"
	version = version_el.text.strip() if version_el is not None and version_el.text else "1.0"
	safe_name = "".join(c for c in name if c.isalnum() or c in ("_", "-"))
	return f"{safe_name}_v{version}.zip"


def prepare_build_dir():
	if BUILD_DIR.exists():
		shutil.rmtree(BUILD_DIR)
	BUILD_DIR.mkdir(parents=True)
	DIST_DIR.mkdir(parents=True, exist_ok=True)


def collect_files():
	if not ASSETS_DIR.exists():
		raise FileNotFoundError(f"Resources dir not found: {ASSETS_DIR}")
	shutil.copytree(ASSETS_DIR, BUILD_DIR, dirs_exist_ok=True)
	src_gamedata = SRC_DIR / "gamedata"
	if not src_gamedata.exists():
		raise FileNotFoundError(f"Mod dir not found: {src_gamedata}")
	shutil.copytree(src_gamedata, BUILD_DIR  / "gamedata")
	# Remove files matching *.bkp.*
	for item in BUILD_DIR.rglob("*"):
		if item.is_file() and ".bkp." in item.name:
			item.unlink()


def pack_to_zip(archive_name: str):
	archive_path = DIST_DIR / archive_name
	with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
		for file_path in BUILD_DIR.rglob("*"):
			if file_path.is_file():
				arcname = file_path.relative_to(BUILD_DIR)
				zf.write(file_path, arcname)

	print(f"Build finish: {archive_path}")


def main():
	print("Build start...")
	archive_name = get_archive_name()
	prepare_build_dir()
	collect_files()
	pack_to_zip(archive_name)


if __name__ == "__main__":
	main()