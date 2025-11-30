import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tortoise-tts",
    packages=setuptools.find_packages(),
    version="3.0.0",
    author="James Betker",
    author_email="james@adamant.ai",
    description="A high quality multi-voice text-to-speech library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/neonbjb/tortoise-tts",
    project_urls={},
    scripts=[
        'scripts/tortoise_tts.py',
    ],
    include_package_data=True,
    install_requires=[
        'tqdm',
        'rotary_embedding_torch',
        'inflect',
        'einops==0.4.1',
        'unidecode',
        'numpy==1.23.5',
        'scipy==1.10.1',
        'librosa==0.10.1',
        'numba==0.59.1',
        'llvmlite==0.42.0',
        'transformers==4.31.0',
        'tokenizers>=0.13,<0.15',
        'flask',
        'soundfile==0.12.1',
        'torchaudio',
        'threadpoolctl',
        'appdirs',
        'pydantic==1.9.1',
        'py-cpuinfo',
        'hjson',
        'psutil',
        'sounddevice',
        'spacy==3.7.5',
    ],
    extras_require={
        'deepspeed': ['deepspeed>=0.10.0; platform_system != "Windows"']
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10,<3.12",
)
