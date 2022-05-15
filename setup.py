from setuptools import setup
import re


requirements = []
with open('requirements.txt') as f:
  requirements = f.read().splitlines()


version: str = ''
with open('discord/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)  # type: ignore


if not version:
    raise RuntimeError('version is not set')


if version.endswith(('a', 'b', 'rc')):
    # append version identifier based on commit count
    try:
        import subprocess
        p = subprocess.Popen(['git', 'rev-list', '--count', 'HEAD'],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if out:
            version += out.decode('utf-8').strip()
        p = subprocess.Popen(['git', 'rev-parse', '--short', 'HEAD'],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if out:
            version += '+g' + out.decode('utf-8').strip()
    except Exception:
        pass


readme = ''
with open('README.rst') as f:
    readme = f.read()


extras_require = {
    'voice': [
        'PyNaCl>=1.3.0,<1.5',
    ],
    'docs': [
        'sphinx==4.0.2',
        'sphinxcontrib_trio==1.1.2',
        'sphinxcontrib-websupport',
    ],
    'speed': [
        'orjson>=3.5.4',
        'aiodns>=1.1',
        'Brotli',
        'cchardet',
    ],
    'vbu': [
        # Main build
        "toml",
        "aiosqlite",
        "aioredis>=1.3,<2.0",
        "aioredlock>=0.7.0,<0.8",
        "aiodogstatsd>=0.14.0,<0.15",
        "upgradechatpy>=1.0.3<2.0",

        # Web build
        "cryptography",
        "aiohttp_jinja2",
        "aiohttp_session",
        "jinja2>=3.0.0,<4.0.0",
        "markdown",
        "htmlmin",
    ]
}


packages = [
    'discord',
    'discord.types',
    'discord.ui',
    'discord.webhook',
    'discord.ext.commands',
    'discord.ext.tasks',

    'discord.ext.vbu',
    'discord.ext.vbu.cogs',
    'discord.ext.vbu.cogs.utils',
    'discord.ext.vbu.cogs.utils.checks',
    'discord.ext.vbu.cogs.utils.converters',
    'discord.ext.vbu.cogs.utils.database',
    'discord.ext.vbu.cogs.utils.menus',
    'discord.ext.vbu.cogs.utils.types',
    'discord.ext.vbu.web',
    'discord.ext.vbu.web.utils',
    'voxelbotutils',
]


setup(
    name='novus',
    author='Kae Bartlett',
    url='https://github.com/Voxel-Fox-Ltd/Novus',
    project_urls={
        "Documentation": "https://novus.readthedocs.io/en/latest/",
        "Issue tracker": "https://github.com/Voxel-Fox-Ltd/Novus/issues",
    },
    version=version,
    packages=packages,
    license='MIT',
    description='A Python wrapper for the Discord API',
    long_description=readme,
    long_description_content_type="text/x-rst",
    include_package_data=True,
    install_requires=requirements,
    extras_require=extras_require,
    python_requires='>=3.8.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'Typing :: Typed',
    ],
    entry_points={
        "console_scripts": [
            "voxelbotutils=discord.ext.vbu.__main__:main",
            "vbu=discord.ext.vbu.__main__:main",
        ],
    },
    package_data={
        "discord.ext.vbu": ["config/*"]
    },
)
