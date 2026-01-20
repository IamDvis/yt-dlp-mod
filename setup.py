from setuptools import setup


setup(
    name="yt-dlp-mod",
    version="0.4.0",
    license="The Unlicense",
    author="IamDvis",
    maintainer="IamDvis",
    author_email="iamdvis@proton.me",
    description="An extension of yt-dlp targeting YoutubeDL with pydantic support.",
    packages=["yt_dlp_mod"],
    url="https://github.com/IamDvis/yt-dlp-mod",
    project_urls={
        "Bug Report": "https://github.com/IamDvis/yt-dlp-mod/issues/new",
        "Homepage": "https://github.com/IamDvis/yt-dlp-mod",
        "Source Code": "https://github.com/IamDvis/yt-dlp-mod",
        "Issue Tracker": "https://github.com/IamDvis/yt-dlp-mod/issues",
        "Download": "https://github.com/IamDvis/yt-dlp-mod/releases",
        "Documentation": "https://github.com/IamDvis/yt-dlp-mod/",
    },
    entry_points={
        "console_scripts": ["yt-dlpm = yt_dlp_mod.cli:app"],
    },
    install_requires=["yt-dlp>=2025.7.21", "pydantic>=2.11.7", "typer>=0.16.0"],
    python_requires=">=3.10",
    keywords=[
        "yt-dlp",
        "yt-dlp-mod",
    ],
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "License :: OSI Approved :: The Unlicense (Unlicense)",
        "Intended Audience :: Developers",
        "License :: Free For Home Use",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
